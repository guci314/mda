# PIM UI - Web Interface for PIM Engine

A modern web interface for managing PIM (Platform Independent Model) models and instances.

## Overview

PIM UI is a separated frontend application that provides a user-friendly interface for:
- Model management (upload, view, delete)
- Instance management (create, monitor, control)
- Real-time compilation progress tracking
- Debug interface for flow visualization

## Architecture

- **Frontend**: Pure HTML/CSS/JavaScript (no framework dependencies)
- **Backend**: Express.js server for serving static files
- **Communication**: REST API calls to PIM Engine (port 8000)

## Installation

```bash
# Install dependencies
npm install

# Start the server
npm start
```

The UI will be available at http://localhost:3000

## Features

### Model Management
- Upload PIM models (YAML/Markdown formats)
- View loaded models with metadata
- Hard unload models (with file cleanup)
- Real-time compilation progress tracking
- Visual feedback for long-running operations

### Instance Management
- Create instances from loaded models
- Monitor instance status and health
- Start/stop instances
- View instance metrics (port, PID, uptime)
- Access instance API documentation

### Debug Interface
- Visual flow debugging
- Mermaid diagram rendering
- Step-by-step execution tracking

## Configuration

Create a `.env` file for custom configuration:

```env
PORT=3000                    # UI server port
API_BASE_URL=http://localhost:8000  # PIM Engine URL
```

## API Integration

The UI communicates with PIM Engine through these endpoints:

- `GET /models` - List loaded models
- `POST /models/upload` - Upload new model
- `DELETE /models/{name}` - Unload model
- `GET /instances` - List running instances
- `POST /instances` - Create new instance
- `DELETE /instances/{id}` - Stop instance

## Development

### File Structure
```
pim-ui/
├── public/
│   ├── models.html      # Model management page
│   ├── instances.html   # Instance management page
│   ├── debug.html       # Debug interface
│   └── js/
│       └── config.js    # Shared configuration
├── server.js            # Express server
├── package.json         # Dependencies
└── README.md           # This file
```

### Adding New Features

1. Create new HTML file in `public/`
2. Include shared configuration: `<script src="/js/config.js"></script>`
3. Use `API_BASE_URL` for API calls
4. Follow existing UI patterns for consistency

## Troubleshooting

### CORS Issues
The Express server includes CORS headers. If you still face issues:
1. Check that PIM Engine is running on port 8000
2. Verify no proxy settings interfering
3. Use `--noproxy localhost` with curl commands

### Upload Issues
- Ensure PIM Engine has write permissions to models directory
- Check that model files are valid YAML/Markdown
- Monitor browser console for detailed errors

## Future Improvements

- [ ] Add authentication/authorization
- [ ] Implement WebSocket for real-time updates
- [ ] Add model syntax validation
- [ ] Create visual model editor
- [ ] Add dark mode support