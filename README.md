# KnowBe4 Static API Replica

This project is a static replica of the KnowBe4 Help Center API (Zendesk V2), built using [Hugo](https://gohugo.io/) and hosted on GitHub Pages. It serves static JSON files that mimic the structure and content of the real API endpoints.

## How It Works

1.  **Data Source**: The core data is stored in JSON files within the `site_src/data/zendesk/` directory:
    *   `categories.json`
    *   `sections.json`
    *   `articles.json`
    These files contain the actual data fetched from the KnowBe4 Help Center.

2.  **Hugo Templating**: Hugo uses layout templates located in `site_src/layouts/api/` to process this data.
    *   Instead of rendering HTML, these templates use Hugo's `jsonify` function to output the data directly as valid JSON.
    *   The templates are mapped to specific URLs using content stubs in `site_src/content/api/v2/help_center/en-us/`.

3.  **Deployment**:
    *   A GitHub Actions workflow (`.github/workflows/hugo.yaml`) triggers on every push to the `main` branch.
    *   It builds the Hugo site and deploys the generated `public/` directory to the `gh-pages` branch.
    *   GitHub Pages serves these static files, making them accessible via public URLs.

## API URLs for Google GEMs

Use the following URLs to access the static API endpoints. These are the URLs you should provide to your Google GEMs or other tools that need to consume this data.

### Base URL
`https://Criscras13.github.io/API_testing/`

### Endpoints

*   **Categories**:
    ```
    https://Criscras13.github.io/API_testing/api/v2/help_center/en-us/categories.json
    ```

*   **Sections**:
    ```
    https://Criscras13.github.io/API_testing/api/v2/help_center/en-us/sections.json
    ```

*   **Articles**:
    ```
    https://Criscras13.github.io/API_testing/api/v2/help_center/en-us/articles.json
    ```

*   **Individual Articles**:
    Individual articles are accessible in two formats:
    
    **JSON Format** (for API clients):
    ```
    https://Criscras13.github.io/API_testing/api/v2/help_center/en-us/articles/{id}.json
    ```
    
    **HTML Wrapper** (for AI agents/browsers):
    The `html_url` field in the article lists points to HTML wrapper pages that display the JSON data in a `<pre>` tag. This allows AI browsing tools (like Google GEMs) to access the content as a "webpage" rather than raw JSON.
    ```
    https://Criscras13.github.io/API_testing/api/v2/help_center/en-us/articles/{id}.html
    ```

### For AI Agents/Browsers

If you are using an AI agent or tool that requires HTML content (like Google GEMs), use the following HTML wrapper URLs that display the JSON data in a browsable format:

*   **Categories (HTML)**:
    ```
    https://Criscras13.github.io/API_testing/api/v2/help_center/en-us/categories.html
    ```

*   **Sections (HTML)**:
    ```
    https://Criscras13.github.io/API_testing/api/v2/help_center/en-us/sections.html
    ```

*   **Articles (HTML)**:
    ```
    https://Criscras13.github.io/API_testing/api/v2/help_center/en-us/articles.html
    ```

*   **Individual Articles (HTML)**:
    ```
    https://Criscras13.github.io/API_testing/api/v2/help_center/en-us/articles/{id}.html
    ```

These HTML endpoints display the same JSON data but wrapped in HTML, making them accessible to AI browsing tools that cannot read raw JSON files.

## Updating Data

To update the data served by this API:

1.  **Run the Data Transformer**:
    This project includes a Python script `data_transformer.py` that fetches fresh data from the KnowBe4 API, rewrites the URLs to point to this GitHub Pages site, and saves the JSON files.
    ```bash
    python data_transformer.py
    ```
    *Note: This script requires internet access to reach `support.knowbe4.com`.*

2.  **Commit and Push**:
    After the script completes, commit the updated files in `site_src/data/zendesk/` and `site_src/static/` and push to the `main` branch.
    ```bash
    git add site_src/data/zendesk/ site_src/static/
    git commit -m "Update API data"
    git push origin main
    ```

3.  **Automatic Deployment**:
    The GitHub Actions workflow will automatically rebuild the site and deploy the updated data to GitHub Pages.
