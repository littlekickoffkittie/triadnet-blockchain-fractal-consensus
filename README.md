# TriadNet Mining Dashboard

A real-time blockchain mining dashboard with fractal visualization for the TriadNet proof-of-work system.

## Features

### Real-time Mining Statistics
- Live chain height monitoring
- Dynamic difficulty adjustments
- Real-time mining rewards tracking
- Hash rate visualization
- Network statistics monitoring
- Transaction pool updates
- Mining logs with fractal coordinates

### Interactive Mining Controls
- Start/Stop mining operations
- Worker thread management
- Mining algorithm selection
- Real-time status feedback

### Visual Elements
- Sierpinski triangle background animation
- Glass-morphism UI design
- Real-time data visualization
- Responsive layout
- Status indicators

## Technical Architecture

### Frontend
- Pure HTML/CSS/JavaScript implementation
- Tailwind CSS for styling
- WebSocket client for real-time updates
- Canvas-based fractal visualization
- Responsive glass-morphism design

### Backend
- Python WebSocket server
- Real-time data processing
- Mining operation management
- Transaction pool handling
- Network statistics aggregation

## Getting Started

1. Start the WebSocket server:
```bash
python3 dashboard_server.py
```

2. Start the HTTP server:
```bash
python3 -m http.server 8000
```

3. Open the dashboard:
```
http://localhost:8000/index.html
```

## Dependencies

### Frontend
- Tailwind CSS (via CDN)
- Google Fonts (Fira Code, Orbitron)
- Font Awesome icons

### Backend
- Python 3.10+
- websockets library (`pip install websockets`)

## Architecture Details

### WebSocket Communication
- Server runs on `ws://localhost:8765`
- Real-time bidirectional communication
- Automatic reconnection handling
- Data refresh every 3 seconds

### Data Flow
1. Client establishes WebSocket connection
2. Server streams mining statistics
3. Client updates UI in real-time
4. Mining controls send commands to server
5. Server processes commands and updates state

### File Structure
```
├── index.html          # Main dashboard interface
├── dashboard.js        # Frontend controller
├── sierpinski.js       # Fractal visualization
├── dashboard_server.py # WebSocket server
└── README.md          # Documentation
```

## Development

### Running in Development Mode
1. Clone the repository
2. Install dependencies: `pip install websockets`
3. Start WebSocket server: `python3 dashboard_server.py`
4. Start HTTP server: `python3 -m http.server 8000`
5. Open browser at `http://localhost:8000`

### Architecture Components

#### Frontend Controller (dashboard.js)
- WebSocket connection management
- UI state management
- Real-time data handling
- Mining control interface

#### Fractal Visualization (sierpinski.js)
- Canvas-based rendering
- Dynamic scaling and rotation
- GPU-accelerated animations
- Responsive design integration

#### WebSocket Server (dashboard_server.py)
- Real-time data streaming
- Mining operation control
- Transaction pool management
- Network statistics aggregation

## Production Deployment Notes

1. Replace Tailwind CSS CDN with production build
2. Configure proper WebSocket security
3. Set up proper process management
4. Implement proper error logging
5. Add monitoring and analytics

## Security Considerations

1. WebSocket connection security
2. Mining operation validation
3. Data integrity verification
4. Access control implementation
5. Error handling and logging

## Future Enhancements

1. Advanced fractal visualizations
2. Enhanced mining analytics
3. Network topology visualization
4. Performance optimization
5. Additional mining algorithms

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## License

MIT License - See LICENSE file for details
