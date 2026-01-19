# SEO Configuration

This document describes the SEO setup for ParserWiz (www.parserwiz.app).

## Overview

SEO elements were added to improve discoverability through search engines and social media sharing.

## Files Created

| File | Purpose |
|------|---------|
| `frontend/robots.txt` | Instructs search engine crawlers |
| `frontend/sitemap.xml` | Lists all pages for search engines |
| `frontend/favicon.svg` | Modern SVG favicon (primary) |
| `frontend/favicon-16x16.png` | Classic small favicon |
| `frontend/favicon-32x32.png` | Classic favicon |
| `frontend/apple-touch-icon.png` | iOS home screen icon (180x180) |
| `frontend/og-image.svg` | Source file for OG image |
| `frontend/og-image.png` | Social media preview image (1200x630) |

## Meta Tags Added to index.html

### Basic SEO

```html
<meta name="description" content="Free online tool to convert JSON, CSV, and Excel files instantly. No signup required. Transform data formats, preview before download, handle complex nested JSON structures.">
<meta name="keywords" content="JSON to CSV, CSV to JSON, Excel converter, data conversion, JSON to Excel, CSV to Excel, file converter, data transformation, online converter">
<meta name="author" content="ParserWiz">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://www.parserwiz.app/">
```

### Search Engine Verification

```html
<meta name="google-site-verification" content="FZ7K4qZyUC4izZpHw8CaJ-K9-zFRlPV9YUZEDMtwlD4">
```

Note: Bing was configured by importing from Google Search Console, so no separate Bing meta tag is required.

### Open Graph (Facebook, LinkedIn)

```html
<meta property="og:type" content="website">
<meta property="og:url" content="https://www.parserwiz.app/">
<meta property="og:title" content="ParserWiz - Convert JSON, CSV, Excel Files Online Free">
<meta property="og:description" content="Free online tool to convert JSON, CSV, and Excel files instantly. No signup required. Transform data formats with live preview.">
<meta property="og:image" content="https://www.parserwiz.app/og-image.png">
<meta property="og:site_name" content="ParserWiz">
```

### Twitter Cards

```html
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:url" content="https://www.parserwiz.app/">
<meta name="twitter:title" content="ParserWiz - Convert JSON, CSV, Excel Files Online Free">
<meta name="twitter:description" content="Free online tool to convert JSON, CSV, and Excel files instantly. No signup required.">
<meta name="twitter:image" content="https://www.parserwiz.app/og-image.png">
```

### Favicon Links

```html
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
```

## Structured Data (JSON-LD)

A WebApplication schema is included in index.html:

```json
{
    "@context": "https://schema.org",
    "@type": "WebApplication",
    "name": "ParserWiz",
    "description": "Free online tool to convert JSON, CSV, and Excel files instantly. No signup required.",
    "url": "https://www.parserwiz.app/",
    "applicationCategory": "UtilitiesApplication",
    "operatingSystem": "Any",
    "offers": {
        "@type": "Offer",
        "price": "0",
        "priceCurrency": "USD"
    },
    "featureList": [
        "JSON to CSV conversion",
        "CSV to JSON conversion",
        "Excel to JSON conversion",
        "JSON to Excel conversion",
        "CSV to Excel conversion",
        "Excel to CSV conversion",
        "Data preview before download",
        "Complex nested JSON handling"
    ]
}
```

## Search Engine Registration

### Google Search Console

- URL: https://search.google.com/search-console
- Status: Verified via HTML meta tag
- Sitemap: Submitted at `https://www.parserwiz.app/sitemap.xml`

### Bing Webmaster Tools

- URL: https://www.bing.com/webmasters
- Status: Verified (imported from Google Search Console)
- Sitemap: Submit at `https://www.parserwiz.app/sitemap.xml`

## Testing Tools

Use these tools to validate your SEO setup:

| Tool | URL | Purpose |
|------|-----|---------|
| Google Rich Results Test | https://search.google.com/test/rich-results | Validate structured data |
| Facebook Sharing Debugger | https://developers.facebook.com/tools/debug/ | Preview OG tags |
| Twitter Card Validator | https://cards-dev.twitter.com/validator | Preview Twitter cards |
| Google PageSpeed Insights | https://pagespeed.web.dev/ | Performance metrics |

## Maintenance

### When to Update

- **sitemap.xml**: Update `<lastmod>` date when significant content changes
- **og-image.png**: Update if branding changes
- **Meta description**: Update if app features change significantly

### Regenerating Favicons

If you need to regenerate favicon PNGs from the SVG:

```bash
cd frontend
rsvg-convert -w 16 -h 16 favicon.svg -o favicon-16x16.png
rsvg-convert -w 32 -h 32 favicon.svg -o favicon-32x32.png
rsvg-convert -w 180 -h 180 favicon.svg -o apple-touch-icon.png
```

### Regenerating OG Image

```bash
cd frontend
rsvg-convert -w 1200 -h 630 og-image.svg -o og-image.png
```
