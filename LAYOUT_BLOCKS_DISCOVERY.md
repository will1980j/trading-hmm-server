# 🔍 LAYOUT.HTML TEMPLATE BLOCKS DISCOVERY (READ-ONLY)

## 📊 COMPLETE BLOCK INVENTORY

**File:** `templates/layout.html`  
**Status:** Minified single-line file  
**Total Blocks Found:** 4

---

## 1️⃣ BLOCK: `page_title`

**Location:** `<head>` section  
**Purpose:** Page title customization  
**Default Value:** "Second Skies Trading"

**Context (10 lines):**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{% block page_title %}Second Skies Trading{% endblock %}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Global Design System -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/platform.css') }}">
    {% block extra_head %}{% endblock %}
```

**Usage Example:**
```jinja
{% block page_title %}Time Analysis — Second Skies{% endblock %}
```

---

## 2️⃣ BLOCK: `extra_head` ⭐ **CUSTOM SCRIPTS BLOCK**

**Location:** `<head>` section (after CSS)  
**Purpose:** Additional head content (CSS, scripts, meta tags)  
**Default Value:** Empty

**Context (10 lines):**
```html
    <meta charset="UTF-8">
    <title>{% block page_title %}Second Skies Trading{% endblock %}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Global Design System -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/platform.css') }}">
    {% block extra_head %}{% endblock %}
</head>
<body class="body--app">
    <div class="app-shell">
        <!-- Header -->
```

**Usage Example:**
```jinja
{% block extra_head %}
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-chart-matrix@3.0.0-beta.2/dist/chartjs-chart-matrix.umd.min.js"></script>
{% endblock %}
```

**✅ THIS IS THE BLOCK FOR CUSTOM HEAD SCRIPTS (CDN libraries, Chart.js, etc.)**

---

## 3️⃣ BLOCK: `content`

**Location:** `<main>` section  
**Purpose:** Main page content  
**Default Value:** Empty

**Context (10 lines):**
```html
        <a href="/reporting-hub" class="app-nav-link">📊 Reports</a>
    </div>
</nav>

<!-- Main Content -->
<main class="app-main">
    {% block content %}{% endblock %}
</main>

</div>
```

**Usage Example:**
```jinja
{% block content %}
<div class="container">
    <h1>Dashboard Content</h1>
</div>
{% endblock %}
```

---

## 4️⃣ BLOCK: `extra_js`

**Location:** Before closing `</body>` tag (after Bootstrap JS)  
**Purpose:** Additional JavaScript at end of page  
**Default Value:** Empty

**Context (10 lines):**
```html
<!-- Main Content -->
<main class="app-main">
    {% block content %}{% endblock %}
</main>

</div>

{% block extra_js %}{% endblock %}

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

**Usage Example:**
```jinja
{% block extra_js %}
<script src="{{ url_for('static', filename='js/time_analysis.js') }}"></script>
<script>
    document.addEventListener('DOMContentLoaded', function() {
        const timeAnalysis = new TimeAnalysis();
        timeAnalysis.init();
    });
</script>
{% endblock %}
```

---

## 🎯 SUMMARY: BLOCK USAGE GUIDE

### **For Custom Head Scripts (CDN Libraries):**
✅ **USE:** `{% block extra_head %}`
- Chart.js, D3.js, matrix plugins
- External CSS libraries
- Meta tags, favicons

### **For Page Title:**
✅ **USE:** `{% block page_title %}`
- Custom page titles

### **For Main Content:**
✅ **USE:** `{% block content %}`
- Dashboard HTML structure
- Page-specific content

### **For Page-Specific JavaScript:**
✅ **USE:** `{% block extra_js %}`
- Custom JavaScript files
- Inline initialization scripts
- Event listeners

---

## 📋 LAYOUT.HTML STRUCTURE OVERVIEW

```
<!DOCTYPE html>
<html>
<head>
    <title>{% block page_title %}</title>
    <meta viewport>
    <link bootstrap CSS>
    <link platform.css>
    {% block extra_head %}  ← CDN SCRIPTS GO HERE
</head>
<body>
    <div class="app-shell">
        <header>...</header>
        <nav>...</nav>
        <main>
            {% block content %}  ← PAGE CONTENT GOES HERE
        </main>
    </div>
    {% block extra_js %}  ← PAGE SCRIPTS GO HERE
    <script bootstrap.js>
</body>
</html>
```

---

## ✅ CONFIRMATION: CUSTOM SCRIPTS BLOCK

**Block Name:** `extra_head`  
**Location:** Inside `<head>`, after platform CSS  
**Purpose:** Custom head content including CDN scripts  
**Used For:** Chart.js, matrix plugins, D3.js, external libraries

**This is the correct block for adding Chart.js and chartjs-chart-matrix CDN scripts.**

---

**END OF DISCOVERY REPORT**
