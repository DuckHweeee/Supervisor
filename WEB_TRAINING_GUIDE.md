# Smart Building AI - Web Training Guide

## 🌐 Overview
The Smart Building AI Assistant now supports training from internet sources! You can enhance the AI's knowledge by adding content from websites, documentation, and online resources related to building management.

## 🚀 Quick Start

### 1. Install Required Dependencies
```bash
pip install requests beautifulsoup4 feedparser urllib3 certifi
```

### 2. Basic Web Training
```python
# Train from a single URL
add_web_content("https://www.energystar.gov/buildings", "energy_standards")

# Train from multiple authoritative websites
train_from_web()

# Get suggestions for training URLs
get_training_url_suggestions()
```

### 3. Interactive Training
```bash
python web_training_demo.py
```

## 📚 Training Sources

### 🏢 Recommended Building Management Websites

#### **Standards & Guidelines:**
- **ASHRAE** (https://www.ashrae.org) - HVAC industry standards
- **USGBC** (https://www.usgbc.org) - LEED green building certification
- **ENERGY STAR** (https://www.energystar.gov) - Energy efficiency guidelines
- **EPA Energy** (https://www.epa.gov/energy) - Environmental energy standards

#### **Smart Building Technologies:**
- **Automated Buildings** (https://www.automatedbuildings.com) - Building automation
- **Intelligent Buildings** (https://www.intelligentbuildings.com) - Smart technologies
- **Smart Buildings Magazine** (https://www.smartbuildingsmagazine.com) - Industry trends
- **BACnet International** (https://www.bacnet.org) - Building automation protocols

#### **HVAC & Systems:**
- **Facilities Net** (https://www.facilitiesnet.com) - Facility management
- **Buildings.com** (https://www.buildings.com) - Building systems
- **Contracting Business** (https://www.contractingbusiness.com) - HVAC practices
- **ACHR News** (https://www.achr-news.com) - Air conditioning & refrigeration

#### **Energy & Sustainability:**
- **Green Biz** (https://www.greenbiz.com) - Sustainable practices
- **Building Green** (https://www.buildinggreen.com) - Environmental strategies
- **NREL** (https://www.nrel.gov) - Renewable energy research
- **DOE Buildings** (https://www.energy.gov/eere/buildings) - Energy efficiency

## 🛠️ Available Functions

### `add_web_content(url, category)`
Add content from a single URL to the knowledge base.

**Parameters:**
- `url`: The website URL to extract content from
- `category`: Category for organizing the content (e.g., "hvac_standards", "energy_efficiency")

**Example:**
```python
add_web_content("https://www.ashrae.org/standards", "hvac_standards")
```

### `train_from_web(custom_urls=None)`
Train from multiple authoritative building websites.

**Parameters:**
- `custom_urls`: Optional list of custom URLs. If not provided, uses default authoritative sources.

**Example:**
```python
# Use default authoritative sources
train_from_web()

# Use custom URLs
custom_sites = [
    "https://www.energystar.gov/buildings",
    "https://www.usgbc.org/leed"
]
train_from_web(custom_sites)
```

### `get_training_url_suggestions()`
Get recommendations for URLs to enhance building management knowledge.

## 🔒 Ethical Guidelines

### ✅ **Best Practices:**
- Only use publicly accessible content
- Respect robots.txt files and rate limits
- Focus on educational and industry-standard resources
- Use authoritative sources (government, industry organizations)
- Attribute content sources properly

### ❌ **Avoid:**
- Copyrighted or proprietary content
- Personal or private information
- Content behind paywalls
- Excessive scraping of single sites
- Non-building-related content

## 🎯 Training Categories

Organize your web training by category:

- **`hvac_standards`** - HVAC guidelines and standards
- **`energy_efficiency`** - Energy optimization practices
- **`building_automation`** - Smart building technologies
- **`green_building`** - Sustainability and LEED practices
- **`safety_security`** - Building safety and security systems
- **`maintenance`** - Equipment maintenance procedures
- **`regulations`** - Building codes and compliance

## 📊 Monitoring Training Progress

### Check Knowledge Base Status:
```python
get_kb_stats()  # View total documents and chunks
```

### Test Enhanced Knowledge:
```python
# Test specific topics after training
search_building_info("LEED certification requirements")
search_building_info("ASHRAE HVAC standards")
search_building_info("building automation best practices")
```

## 🔧 Technical Details

### Supported Content Types:
- **HTML Pages** - Extracts main content, removes navigation/ads
- **RSS/Atom Feeds** - Parses feed entries and summaries
- **Plain Text** - Direct text content
- **PDF** - Basic PDF support (file-based only currently)

### Content Processing:
1. **URL Validation** - Checks accessibility and robots.txt compliance
2. **Content Extraction** - Intelligently extracts meaningful content
3. **Text Chunking** - Splits content into digestible chunks
4. **Embedding Generation** - Creates searchable embeddings
5. **Metadata Addition** - Tracks source URLs and categories

### Rate Limiting:
- 1-second delay between requests
- Respects server rate limits
- Follows robots.txt guidelines

## 🚀 Advanced Usage

### Batch Training Script:
```python
# Create a comprehensive training plan
training_plan = {
    "hvac_standards": [
        "https://www.ashrae.org/technical-resources/standards-and-guidelines",
        "https://www.facilitiesnet.com/hvac"
    ],
    "energy_efficiency": [
        "https://www.energystar.gov/buildings",
        "https://www.energy.gov/eere/buildings"
    ],
    "green_building": [
        "https://www.usgbc.org/leed",
        "https://www.greenbiz.com"
    ]
}

# Execute training plan
for category, urls in training_plan.items():
    for url in urls:
        add_web_content(url, category)
        print(f"Trained from {url} in category {category}")
```

### Custom Content Filtering:
```python
# Add metadata for better organization
add_web_content(
    "https://www.ashrae.org/standards", 
    "hvac_standards",
    metadata={
        "importance": "high",
        "last_updated": "2025-01-01",
        "content_type": "technical_standard"
    }
)
```

## 🎉 Benefits of Web Training

1. **🔄 Real-time Updates** - Access to latest industry standards and practices
2. **📈 Expanded Knowledge** - Comprehensive coverage of building management topics
3. **🏆 Authoritative Sources** - Training from industry leaders and standards organizations
4. **🌍 Global Perspectives** - Access to international best practices
5. **💡 Latest Trends** - Stay current with smart building innovations

## 🛡️ Security & Privacy

- No personal data is collected from websites
- Content is processed locally
- Respects website terms of service
- Follows ethical web scraping practices
- All data stays within your knowledge base

## 📞 Support

For questions about web training:
1. Check this guide for common scenarios
2. Run the demo script for interactive examples
3. Test with small URLs before large-scale training
4. Monitor training results and adjust as needed

---

**🌟 Start enhancing your Smart Building AI with web training today!**
