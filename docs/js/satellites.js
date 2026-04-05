/**
 * Hydrates #repo-list from docs/config/master.yaml (synced copy of repo root manifest).
 * Uses esm.sh yaml parser — no build step. Agents: run scripts/sync-manifest.sh after editing config/master.yaml.
 */
import { parse } from "https://esm.sh/yaml@2.3.4";

function domainLabel(domains, id) {
  const row = domains.find((d) => d.id === id);
  return row ? row.label : id;
}

function renderList(manifest) {
  const ul = document.getElementById("repo-list");
  const status = document.getElementById("repo-list-status");
  if (!ul) return;

  const repos = Array.isArray(manifest.repositories) ? manifest.repositories : [];
  const domains = Array.isArray(manifest.domains) ? manifest.domains : [];

  ul.innerHTML = "";

  if (repos.length === 0) {
    const li = document.createElement("li");
    li.className = "repo-list__empty";
    li.textContent =
      "No external repos in the manifest yet. Mac → NixOS inventory and the Nix flake umbrella already live in this repository (see README). Add optional links under repositories in config/master.yaml when you want to surface other projects here.";
    ul.appendChild(li);
    if (status) status.hidden = true;
    return;
  }

  for (const repo of repos) {
    const li = document.createElement("li");
    li.className = "repo-list__item";

    const title = document.createElement("strong");
    const link = document.createElement("a");
    link.href = repo.url || `https://github.com/${repo.github || ""}`;
    link.textContent = repo.id || repo.github || "repo";
    title.appendChild(link);

    const dash = document.createTextNode(" — ");
    const summary = document.createElement("span");
    summary.textContent = repo.summary || "";

    li.appendChild(title);
    li.appendChild(dash);
    li.appendChild(summary);

    if (Array.isArray(repo.domains) && repo.domains.length > 0) {
      const meta = document.createElement("span");
      meta.className = "repo-list__domains";
      const labels = repo.domains.map((id) => domainLabel(domains, id)).join(" · ");
      meta.textContent = ` (${labels})`;
      li.appendChild(meta);
    }

    ul.appendChild(li);
  }

  if (status) {
    status.textContent = `${repos.length} repo${repos.length === 1 ? "" : "s"} from manifest`;
    status.hidden = false;
  }
}

async function main() {
  const url = new URL("config/master.yaml", window.location.href).href;

  const status = document.getElementById("repo-list-status");
  try {
    const res = await fetch(url, { cache: "no-cache" });
    if (!res.ok) throw new Error(`${res.status}`);
    const text = await res.text();
    const manifest = parse(text);
    renderList(manifest);
  } catch (e) {
    const ul = document.getElementById("repo-list");
    if (ul) {
      ul.innerHTML = "";
      const li = document.createElement("li");
      li.className = "repo-list__empty";
      li.textContent =
        "Could not load docs/config/master.yaml (offline or blocked fetch). See the README for sync instructions.";
      ul.appendChild(li);
    }
    if (status) {
      status.textContent = "Manifest unavailable";
      status.hidden = false;
    }
    console.warn("[repos manifest]", e);
  }
}

main();
