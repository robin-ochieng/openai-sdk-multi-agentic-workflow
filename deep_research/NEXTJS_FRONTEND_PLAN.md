# Deep Research Agent - Next.js Frontend Implementation Plan

## 🎯 Project Overview

Create a professional, modern Next.js frontend for the Deep Research Agent with:
- Real-time progress tracking
- Beautiful UI/UX with animations
- Type-safe TypeScript implementation
- Responsive design (mobile-first)
- Dark mode support
- OpenAI trace visualization
- Email preview capabilities

## 🏗️ Architecture

### Tech Stack
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS + shadcn/ui components
- **State Management**: React hooks + Context API
- **API Communication**: Server-Sent Events (SSE) for real-time updates
- **Icons**: Lucide React
- **Animations**: Framer Motion
- **Forms**: React Hook Form + Zod validation

### Project Structure
```
deep_research/
├── frontend/
│   ├── app/
│   │   ├── layout.tsx           # Root layout with providers
│   │   ├── page.tsx             # Main research page
│   │   ├── api/
│   │   │   └── research/
│   │   │       └── route.ts     # API proxy to Python backend
│   │   └── globals.css          # Global styles
│   ├── components/
│   │   ├── ui/                  # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── input.tsx
│   │   │   ├── textarea.tsx
│   │   │   ├── progress.tsx
│   │   │   ├── badge.tsx
│   │   │   ├── tabs.tsx
│   │   │   └── accordion.tsx
│   │   ├── ResearchForm.tsx     # Main research query form
│   │   ├── LiveProgress.tsx     # Real-time progress display
│   │   ├── SearchPlanView.tsx   # Shows planned searches
│   │   ├── SearchResults.tsx    # Display search results
│   │   ├── ReportPreview.tsx    # Markdown report viewer
│   │   ├── TraceViewer.tsx      # OpenAI trace link
│   │   ├── EmailPreview.tsx     # Email content preview
│   │   └── ExampleQueries.tsx   # Quick start examples
│   ├── lib/
│   │   ├── utils.ts             # Utility functions
│   │   ├── api.ts               # API client
│   │   └── types.ts             # TypeScript types
│   ├── hooks/
│   │   ├── useResearch.ts       # Research state management
│   │   └── useTheme.ts          # Dark mode toggle
│   ├── public/
│   │   └── images/
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── next.config.js
│   └── README.md
```

## 🎨 UI/UX Features

### 1. Home Page
- Hero section with gradient background
- Research input with autocomplete suggestions
- Example queries as clickable cards
- Feature highlights (4-agent pipeline, traces, guardrails)

### 2. Research Progress View
- **Step Indicators**: Visual pipeline (1→2→3→4)
- **Live Logs**: Animated, timestamped, color-coded
- **Progress Bar**: Overall completion percentage
- **Status Cards**: Each agent's current status
- **Loading Animations**: Smooth transitions

### 3. Results Display
- **Tabs Interface**:
  - Search Plan (collapsible list)
  - Search Results (accordion with summaries)
  - Full Report (markdown rendered with syntax highlighting)
  - Email Preview (HTML rendered)
  - Trace URL (embedded or link)
- **Copy to Clipboard**: All content sections
- **Download Options**: PDF, Markdown, HTML
- **Share**: Generate shareable link

### 4. Theme & Styling
- **Dark Mode**: Toggle with system preference detection
- **Color Scheme**:
  - Primary: Blue gradient (#3B82F6 → #8B5CF6)
  - Success: Green (#10B981)
  - Warning: Amber (#F59E0B)
  - Error: Red (#EF4444)
- **Typography**: Inter font family
- **Spacing**: Consistent 8px grid system
- **Shadows**: Soft, layered elevation
- **Animations**: Smooth 200-300ms transitions

## 🔌 Backend Integration

### API Endpoints

#### 1. POST /api/research
Start a new research query with SSE streaming

**Request:**
```json
{
  "query": "Latest AI frameworks 2025"
}
```

**Response (SSE Stream):**
```
event: planning
data: {"step": 1, "status": "Planning searches", "searches": [...]}

event: searching
data: {"step": 2, "status": "Search 1/5", "query": "...", "progress": 0.2}

event: writing
data: {"step": 3, "status": "Writing report", "progress": 0.6}

event: emailing
data: {"step": 4, "status": "Sending email", "progress": 0.9}

event: complete
data: {"report": "...", "trace_url": "...", "email_sent": true}

event: error
data: {"message": "Error details"}
```

#### 2. GET /api/examples
Get example queries

#### 3. GET /api/status
Health check

## 🚀 Implementation Phases

### Phase 1: Setup & Infrastructure (Files 1-10)
1. Initialize Next.js project
2. Setup Tailwind CSS
3. Configure TypeScript
4. Install dependencies
5. Create folder structure
6. Setup environment variables

### Phase 2: Core Components (Files 11-20)
7. Create layout components
8. Build UI component library (shadcn/ui)
9. Implement form components
10. Create progress display

### Phase 3: Features (Files 21-30)
11. Build research form
12. Implement SSE client
13. Create live progress tracker
14. Build result viewers
15. Add markdown renderer

### Phase 4: Polish (Files 31-40)
16. Add animations
17. Implement dark mode
18. Add error handling
19. Create loading states
20. Add responsive design

### Phase 5: Backend Integration (Files 41+)
21. Create API proxy
22. Connect to Python backend
23. Handle streaming responses
24. Error recovery & retry logic

## 📦 Dependencies

```json
{
  "dependencies": {
    "next": "^14.1.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "typescript": "^5.3.0",
    "@radix-ui/react-*": "^1.0.0",
    "tailwindcss": "^3.4.0",
    "framer-motion": "^11.0.0",
    "react-hook-form": "^7.49.0",
    "zod": "^3.22.0",
    "lucide-react": "^0.309.0",
    "react-markdown": "^9.0.0",
    "rehype-highlight": "^7.0.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.0"
  }
}
```

## 🎯 Key Features

### Must-Have
✅ Real-time progress updates via SSE
✅ Responsive design (mobile, tablet, desktop)
✅ Dark mode support
✅ Markdown rendering with syntax highlighting
✅ Copy-to-clipboard functionality
✅ Error handling & retry logic
✅ Loading states & animations
✅ TypeScript type safety

### Nice-to-Have
🎨 Shareable result links
🎨 Export to PDF
🎨 Query history (localStorage)
🎨 Keyboard shortcuts
🎨 Search suggestions
🎨 Analytics dashboard

## 🔒 Security Considerations

- API key never exposed to frontend
- Input validation with Zod
- Rate limiting on API routes
- CORS configuration
- Environment variable protection
- XSS prevention in markdown rendering

## 📊 Performance Targets

- **First Contentful Paint**: < 1.5s
- **Time to Interactive**: < 3s
- **Lighthouse Score**: > 90
- **Bundle Size**: < 200KB (gzipped)
- **API Response**: < 100ms (excluding research time)

## 🧪 Testing Strategy

- **Unit Tests**: Component logic
- **Integration Tests**: API routes
- **E2E Tests**: User flows (Playwright)
- **Type Safety**: Full TypeScript coverage
- **Accessibility**: WCAG 2.1 AA compliance

---

**Total Estimated Files**: ~40 files
**Estimated Implementation Time**: 3-4 hours for full implementation
**Complexity Level**: Professional/Production-Ready
