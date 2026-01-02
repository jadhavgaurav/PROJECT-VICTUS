# PROJECT-VICTUS Frontend

A modern, responsive React application built with TypeScript and Vite. It serves as the user interface for the sophisticated PROJECT-VICTUS AI Agent, featuring real-time chat, voice interaction, and comprehensive system management tools.

## 🚀 Technologies

- **Framework**: [React](https://react.dev/) 18
- **Build Tool**: [Vite](https://vitejs.dev/)
- **Language**: [TypeScript](https://www.typescriptlang.org/)
- **State Management**: [Zustand](https://github.com/pmndrs/zustand)
- **Styling**: [Tailwind CSS](https://tailwindcss.com/)
- **Icons**: [Lucide React](https://lucide.dev/)
- **Routing**: [React Router](https://reactrouter.com/)
- **HTTP Client**: [Axios](https://axios-http.com/)

## ✨ Key Features

- **Real-time Chat Interface**: Streaming responses with optimistic UI updates.
- **Voice Interaction**: Integrated microphone capture and audio playback.
- **File Attachments**: Upload PDF/DOCX files for RAG processing.
- **Tools Dashboard**: Visual interface for Agent approvals, traces, analytics, and visuals.
- **User Settings**: Profile management, memory (facts) control, and security settings.
- **Responsive Design**: Optimized for desktop and efficient usage.

## 🛠️ Setup & Installation

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

1. Navigate to the frontend directory:

   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

### Development

Start the development server:

```bash
npm run dev
```

The application will be available at `http://localhost:5173`. It expects the backend API to be running at `http://localhost:8000`.

### Build

Create a production build:

```bash
npm run build
```

The output will be in the `dist/` directory.

### Linting

Run ESLint to check for code quality:

```bash
npm run lint
```

## 📁 Project Structure

```
src/
├── api/              # API client and endpoints
├── assets/           # Static assets (images, fonts)
├── components/       # Reusable UI components
│   ├── chat/         # Chat-specific components (Composer, Bubble)
│   ├── layout/       # Layout components (Sidebar, Topbar)
│   └── ui/           # Generic UI primitives (Button, Modal)
├── context/          # React Context (Auth)
├── hooks/            # Custom React hooks
├── state/            # Zustand stores (Agent state)
├── types/            # TypeScript type definitions
├── utils/            # Helper functions
└── App.tsx           # Main application component
```

## 🔐 Configuration

The application authenticates with the backend using JWT stored in HTTP-only cookies.

- **Base URL**: Configured in `src/api/client.ts`. Defaults to `/api` (proxied in dev).

## 🤝 Contributing

1. Ensure all components are strongly typed.
2. Use Tailwind utility classes for styling.
3. Keep components small and focused.
