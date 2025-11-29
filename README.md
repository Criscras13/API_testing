# API Testing Repository

> ⚠️ **EXPERIMENTAL TESTING BRANCH**: This branch contains Phase 8 image indexing features under development.  
> **For stable production API**, see [main branch](https://github.com/Criscras13/API_testing/tree/main)

---

## 🧪 Phase 8: Experimental Image Metadata & Topic Indexing

This testing branch includes experimental AI-powered image search and metadata indexing capabilities.

### **What's New in This Branch**

- ✅ **3,519 images indexed** with AI-generated descriptions
- ✅ **8,908 unique topics** extracted for semantic image search
- ✅ **1,004 enhanced articles** with image metadata
- ✅ Full absolute URLs for all resources
- ✅ Backward-compatible (production endpoints unchanged)

### **Testing Endpoints (HTML for GEMs)**

Use these URLs for your AI Agents (GEMs). They work exactly like your production URLs but point to the new experimental data:

*   **Experimental Articles List:**
    ```
    https://Criscras13.github.io/API_testing/api/v2/help_center/en-us/experimental/articles.html
    ```

*   **Image Index (New!):**
    ```
    https://Criscras13.github.io/API_testing/api/v2/help_center/en-us/experimental/image_index.html
    ```

*   **Topic Index (New!):**
    ```
    https://Criscras13.github.io/API_testing/api/v2/help_center/en-us/experimental/topics_to_images.html
    ```

*   **Experimental Article Detail:**
    ```
    https://Criscras13.github.io/API_testing/api/v2/help_center/en-us/experimental/articles/{id}.html
    ```

### **Testing Endpoints (JSON for Developers)**

All experimental features are isolated in the `/experimental/` directory:

```
https://Criscras13.github.io/API_testing/api/v2/help_center/en-us/experimental/
├── image_index.json         # Global image-to-metadata index (~29 MB)
├── topics_to_images.json    # Topic-to-images reverse index (~2.3 GB)
├── articles.json            # List of all enhanced articles
└── articles/
    ├── 217841868.json      # Enhanced article with images array
    └── ... (1,004 articles)
```

### **Example: Enhanced Article Structure**

Each article now includes an `images` array and `metadata` object:

```json
{
  "id": 217841868,
  "title": "Monitor and Review Phishing Campaigns",
  "images": [
    {
      "url": "https://helpimg.s3.us-east-1.amazonaws.com/...",
      "alt": "AI-generated description of image...",
      "position": 1,
      "context": "Surrounding text context"
    }
  ],
  "metadata": {
    "category": "Kevin Mitnick Security Awareness Training",
    "section": "Phishing",
    "topics": ["campaign", "phishing", "security", ...],
    "image_count": 15
  }
}
```

### **Testing with GEMs**

You can query experimental indexes to retrieve images by:
- **Topic**: Find all images related to "phishing campaigns"
- **Article**: Get all images from a specific article
- **URL**: Look up metadata for a specific image

### **File Sizes**

- `image_index.json`: 29 MB
- `topics_to_images.json`: 2.3 GB (pre-computed for fast lookups)
- Enhanced articles: ~64 KB average

---

## 📚 Production API Documentation

The main API structure remains unchanged and fully functional:

- `/api/v2/help_center/en-us/articles/` - All articles
- `/api/v2/help_center/en-us/categories/` - All categories
- `/api/v2/help_center/en-us/sections/` - All sections

---

## 🔄 Branch Strategy

- **`main`**: Stable production API
- **`phase8-testing`**: Experimental image indexing (this branch)

Once testing is verified successful, experimental features will be merged to `main`.

---

## 📖 Testing Documentation

See [`phase8_verification.md`](https://github.com/Criscras13/API_testing/blob/phase8-testing/.gemini/antigravity/brain/.../phase8_verification.md) for detailed implementation and verification notes.
