# Static Files Directory

This directory contains static files for the Web-Based Project Architect backend.

## Usage

To serve static files, uncomment the following line in `main.py`:

```python
app.mount("/static", StaticFiles(directory="static"), name="static")
```

## Common Static Files

- `css/` - Stylesheets
- `js/` - JavaScript files
- `images/` - Images and icons
- `docs/` - Documentation files

## Example Structure

```
static/
├── css/
│   └── styles.css
├── js/
│   └── app.js
├── images/
│   └── logo.png
└── docs/
    └── api.md
``` 