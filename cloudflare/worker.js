// Cloudflare Worker: dispatch the MAMA Tracker GitHub Actions workflow.
// Store a fine-grained GitHub token in the Worker secret GITHUB_TOKEN.
// The token only needs Actions: write on the mama-tracker repository.

const OWNER = "luisequeira612-commits";
const REPO = "mama-tracker";
const WORKFLOW = "update.yml";
const REF = "main";

export default {
  async scheduled(controller, env) {
    if (!env.GITHUB_TOKEN) {
      throw new Error("Missing Worker secret: GITHUB_TOKEN");
    }

    const endpoint =
      `https://api.github.com/repos/${OWNER}/${REPO}/actions/workflows/${WORKFLOW}/dispatches`;

    const response = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Accept": "application/vnd.github+json",
        "Authorization": `Bearer ${env.GITHUB_TOKEN}`,
        "X-GitHub-Api-Version": "2026-03-10",
        "Content-Type": "application/json",
        "User-Agent": "mama-tracker-cloudflare-scheduler",
      },
      body: JSON.stringify({ ref: REF }),
    });

    if (response.status !== 204) {
      // Do not log the request headers, token, or response body.
      throw new Error(
        `GitHub workflow dispatch failed with HTTP ${response.status}`
      );
    }

    console.log(
      `Dispatched ${OWNER}/${REPO}/${WORKFLOW} for ref ${REF}; scheduled at ${new Date(controller.scheduledTime).toISOString()}`
    );
  },
};
