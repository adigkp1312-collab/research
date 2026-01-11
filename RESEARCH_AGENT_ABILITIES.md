# Research Agent Abilities

**Package:** `packages/research_agent`  
**Service:** `apps/research-service` (Cloud Run)  
**Status:** ✅ Fully Implemented

---

## 🎯 Core Capabilities

### 1. **Internet Research with Google Search Grounding**

The research agent uses **Vertex AI's Google Search grounding** to perform real-time internet research. This means:

- ✅ **Live Web Search**: Uses Google Search to find current information
- ✅ **Real-time Data**: Gets up-to-date information from the internet
- ✅ **Verified Sources**: Returns source URLs for all information
- ✅ **Comprehensive Coverage**: Searches multiple sources automatically

### 2. **Input Types Supported**

- ✅ **URL Research**: Automatically detects and researches URLs
  - Example: `https://nike.com` → Researches the website
  - Auto-detects URLs starting with `http://`, `https://`, or `www.`

- ✅ **Text Query Research**: Researches any text query
  - Example: `"Nike Air Max"` → Researches the product
  - Example: `"Apple Inc company information"` → Researches the company

### 3. **Research Focus Areas**

The agent can research three main areas (configurable):

#### **Product Research**
Extracts structured information about products:
- Product name
- Description
- Features list
- Pricing information
- Unique selling proposition (USP)
- Target audience

#### **Company Research**
Extracts structured information about companies:
- Company name
- About/what the company does
- Founded year
- Headquarters location
- Mission statement
- Social media presence (Instagram, YouTube, etc.)

#### **Market Research**
Provides market intelligence:
- Competitors list with positioning
- Industry trends
- Audience insights (demographics, behavior)
- Market size information

### 4. **Ad/Video Creation Recommendations**

Automatically generates creative recommendations for ad/video production:

- **Key Messages**: Suggested messaging points
- **Emotional Hooks**: Emotional triggers for audience
- **Visual Themes**: Visual style recommendations
- **CTA Suggestions**: Call-to-action ideas

### 5. **Structured JSON Output**

Returns all research in a structured JSON format:

```json
{
  "research_type": "product_research",
  "input": {
    "type": "url",
    "value": "https://example.com"
  },
  "product": { ... },
  "company": { ... },
  "market": { ... },
  "ad_recommendations": {
    "key_messages": [...],
    "emotional_hooks": [...],
    "visual_themes": [...],
    "cta_suggestions": [...]
  },
  "sources": [
    {"url": "https://...", "title": "Source Title"}
  ],
  "generated_at": "2025-01-08T12:00:00Z"
}
```

### 6. **Data Persistence**

- ✅ **Supabase Storage**: Saves all research to Supabase database
- ✅ **Project Association**: Links research to projects
- ✅ **User Tracking**: Tracks who created the research
- ✅ **CRUD Operations**: Full create, read, update, delete support

---

## 🔧 Technical Abilities

### **Vertex AI Integration**

- Uses **Gemini 1.5 Flash** model with Google Search grounding
- Model: `gemini-1.5-flash-002`
- Tool: `GoogleSearchRetrieval()` for real-time search
- Automatic JSON parsing with error handling

### **Smart Input Detection**

- Automatically detects if input is URL or text
- Handles various URL formats
- Fallback to text research if URL detection fails

### **Intelligent Title Generation**

- Generates descriptive titles from research results
- Uses product/company names when available
- Falls back to domain name for URLs
- Truncates long inputs intelligently

### **Error Handling**

- Graceful error handling for research failures
- JSON parsing with markdown code block support
- Fallback error responses
- Detailed error messages

---

## 📡 API Endpoints

### **POST /research**
Create new research from URL or text.

**Capabilities:**
- Accepts URL or text input
- Auto-detects input type
- Configurable research focus (product/company/market)
- Returns full analysis with sources
- Saves to Supabase automatically

### **GET /research/{project_id}**
List all research for a project.

**Capabilities:**
- Returns research list with metadata
- Configurable limit (default: 50)
- Sorted by creation date (newest first)
- Lightweight response (no full analysis data)

### **GET /research/item/{research_id}**
Get single research with full data.

**Capabilities:**
- Returns complete research analysis
- Includes all product/company/market data
- Includes ad recommendations
- Includes source URLs

### **PATCH /research/{research_id}**
Update research data.

**Capabilities:**
- Update analysis data
- Update title
- User ownership validation
- Timestamp tracking

### **DELETE /research/{research_id}**
Delete research entry.

**Capabilities:**
- User ownership validation
- Permanent deletion
- Returns confirmation

---

## 💡 Use Cases

### **1. Product Research for Video Ads**
```
Input: "Nike Air Max 270"
Output: Product features, pricing, target audience, ad recommendations
Use: Create video ad script with key messages
```

### **2. Company Research for Brand Videos**
```
Input: "https://apple.com"
Output: Company info, mission, social presence, market position
Use: Create brand video with accurate company information
```

### **3. Market Research for Campaigns**
```
Input: "smartphone market 2024"
Output: Competitors, trends, audience insights, market size
Use: Plan marketing campaign with market intelligence
```

### **4. Competitive Analysis**
```
Input: Competitor URLs or product names
Output: Competitive positioning, market share, differentiation
Use: Create competitive ad campaigns
```

---

## 🎨 Research Output Structure

### **Product Information**
- Name, description, features
- Pricing and value proposition
- Target audience demographics
- Unique selling points

### **Company Information**
- Company background and history
- Mission and values
- Location and founding details
- Social media presence

### **Market Intelligence**
- Competitor analysis
- Industry trends
- Audience demographics
- Market size and opportunity

### **Creative Recommendations**
- Key messaging points
- Emotional hooks
- Visual themes
- Call-to-action suggestions

### **Source Attribution**
- All sources with URLs
- Source titles
- Verifiable information

---

## ⚙️ Configuration

### **Research Focus Options**

You can specify which areas to research:

```python
# Research all areas (default)
research_focus = ['product', 'company', 'market']

# Research only product
research_focus = ['product']

# Research product and market
research_focus = ['product', 'market']
```

### **Environment Requirements**

- `GOOGLE_CLOUD_PROJECT`: GCP project ID
- `VERTEX_AI_LOCATION`: Region (default: us-central1)
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_SERVICE_KEY`: Supabase service key

---

## 🚀 Deployment Status

- ✅ **Code Complete**: Fully implemented
- ✅ **Cloud Run Ready**: Dockerfile and deployment config ready
- ✅ **Currently Deployed**: `https://research-service-1083011801594.asia-southeast1.run.app`
- ✅ **API Documentation**: Complete

---

## 📊 Example Research Flow

```
1. User provides: "https://nike.com/air-max-270"
2. Agent detects: URL input
3. Vertex AI searches: Google Search grounding finds current info
4. Agent extracts:
   - Product: Air Max 270 features, pricing
   - Company: Nike history, mission
   - Market: Athletic shoe market, competitors
5. Agent generates: Ad recommendations
6. Agent saves: To Supabase with metadata
7. Returns: Structured JSON with all data + sources
```

---

## 🔮 Potential Enhancements (Not Yet Implemented)

- [ ] Multi-language research support
- [ ] Image analysis from URLs
- [ ] Historical research (time-series data)
- [ ] Research comparison (compare multiple products)
- [ ] Research templates (customizable output formats)
- [ ] Batch research (research multiple items at once)
- [ ] Research scheduling (automated periodic research)
- [ ] Research alerts (notify on changes)

---

## 📝 Summary

The Research Agent is a **powerful internet research tool** that:

✅ Uses real-time Google Search via Vertex AI  
✅ Supports both URLs and text queries  
✅ Extracts structured product/company/market data  
✅ Generates ad/video creation recommendations  
✅ Provides source attribution  
✅ Persists data to Supabase  
✅ Offers full CRUD API  

**Perfect for:** Video production research, ad campaign planning, competitive analysis, market intelligence.
