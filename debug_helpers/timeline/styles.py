"""Timeline CSS Styles Module - Contains all CSS styling for timeline visualization."""


def generate_css() -> str:
    """Generate CSS styles for the timeline."""
    return """
    <style>
        :root {
            --bg-primary: #1a1a1a;
            --bg-secondary: #2a2a2a;
            --bg-tertiary: #3a3a3a;
            --text-primary: #ffffff;
            --text-secondary: #b0b0b0;
            --border-color: #444;
            --success-color: #28a745;
            --warning-color: #ffc107;
            --error-color: #dc3545;
            --info-color: #17a2b8;
            --critical-color: #721c24;
        }
        
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
        }
        
        #timeline-app {
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        /* Header Styles */
        .timeline-header {
            background: var(--bg-secondary);
            padding: 20px;
            border-bottom: 1px solid var(--border-color);
        }
        
        .timeline-header h1 {
            margin-bottom: 10px;
            font-size: 24px;
        }
        
        .summary-stats {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }
        
        .stat-item {
            display: flex;
            gap: 8px;
            align-items: center;
        }
        
        .stat-label {
            color: var(--text-secondary);
            font-size: 14px;
        }
        
        .stat-value {
            font-weight: bold;
            font-size: 16px;
        }
        
        .error-count { color: var(--error-color); }
        .warning-count { color: var(--warning-color); }
        .success-count { color: var(--success-color); }
        
        /* Controls */
        .timeline-controls {
            background: var(--bg-secondary);
            padding: 15px 20px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
        }
        
        .filter-controls {
            display: flex;
            gap: 15px;
            align-items: center;
            flex-wrap: wrap;
        }
        
        .filter-group {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .filter-group label {
            font-size: 14px;
            color: var(--text-secondary);
        }
        
        .filter-select, .filter-input {
            background: var(--bg-tertiary);
            color: var(--text-primary);
            border: 1px solid var(--border-color);
            padding: 6px 10px;
            border-radius: 4px;
            font-size: 14px;
        }
        
        .filter-input {
            width: 200px;
        }
        
        .navigation-controls {
            display: flex;
            gap: 10px;
        }
        
        .btn {
            background: var(--bg-tertiary);
            color: var(--text-primary);
            border: 1px solid var(--border-color);
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s;
        }
        
        .btn:hover {
            background: var(--border-color);
        }
        
        .btn-icon {
            padding: 6px 8px;
            font-size: 16px;
        }
        
        .btn-secondary {
            background: transparent;
            color: var(--text-secondary);
        }
        
        /* Timeline Container */
        .timeline-container {
            flex: 1;
            position: relative;
            overflow: hidden;
            background: var(--bg-primary);
        }
        
        .timeline-swimlanes {
            position: absolute;
            left: 0;
            top: 0;
            width: 200px;
            height: 100%;
            background: var(--bg-secondary);
            border-right: 1px solid var(--border-color);
            z-index: 10;
        }
        
        .swimlane {
            height: 80px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            align-items: center;
        }
        
        .swimlane-header {
            padding: 10px 15px;
            width: 100%;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .module-name {
            font-weight: bold;
            font-size: 14px;
        }
        
        .event-count {
            font-size: 12px;
            color: var(--text-secondary);
        }
        
        .timeline-events {
            position: absolute;
            left: 200px;
            top: 0;
            right: 0;
            height: 100%;
            overflow-x: auto;
            overflow-y: hidden;
        }
        
        /* Timeline Events */
        .timeline-event {
            position: absolute;
            width: 4%;
            height: 20px;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 4px;
            transform: translateY(-50%);
        }
        
        .timeline-event:hover {
            z-index: 100;
            transform: translateY(-50%) scale(1.2);
        }
        
        .timeline-event.has-duration {
            border-radius: 10px;
        }
        
        /* Event Severity Colors */
        .severity-info { background: var(--info-color); }
        .severity-success { background: var(--success-color); }
        .severity-warning { background: var(--warning-color); }
        .severity-error { background: var(--error-color); }
        .severity-critical { background: var(--critical-color); }
        
        .event-icon {
            font-size: 14px;
            filter: drop-shadow(0 0 2px rgba(0,0,0,0.5));
        }
        
        /* Tooltip */
        .event-tooltip {
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%) translateY(-5px);
            background: var(--bg-tertiary);
            border: 1px solid var(--border-color);
            border-radius: 4px;
            padding: 10px;
            min-width: 250px;
            display: none;
            z-index: 1000;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        
        .timeline-event:hover .event-tooltip {
            display: block;
        }
        
        .tooltip-header {
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .tooltip-time {
            font-size: 12px;
            color: var(--text-secondary);
            margin-bottom: 5px;
        }
        
        .tooltip-description {
            font-size: 13px;
            color: var(--text-secondary);
        }
        
        /* Details Panel */
        .event-details-panel {
            position: fixed;
            right: -400px;
            top: 0;
            width: 400px;
            height: 100vh;
            background: var(--bg-secondary);
            border-left: 1px solid var(--border-color);
            transition: right 0.3s;
            z-index: 1000;
            overflow-y: auto;
        }
        
        .event-details-panel.open {
            right: 0;
        }
        
        .details-header {
            padding: 20px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .details-header h3 {
            margin: 0;
        }
        
        .btn-close {
            background: none;
            border: none;
            color: var(--text-secondary);
            font-size: 24px;
            cursor: pointer;
            padding: 0;
            width: 30px;
            height: 30px;
        }
        
        .details-content {
            padding: 20px;
        }
        
        .details-placeholder {
            color: var(--text-secondary);
            text-align: center;
            margin-top: 50px;
        }
        
        /* Event Details Styles */
        .event-detail-section {
            margin-bottom: 20px;
        }
        
        .detail-label {
            font-weight: bold;
            color: var(--text-secondary);
            font-size: 12px;
            text-transform: uppercase;
            margin-bottom: 5px;
        }
        
        .detail-value {
            margin-bottom: 15px;
        }
        
        .code-block {
            background: var(--bg-primary);
            border: 1px solid var(--border-color);
            border-radius: 4px;
            padding: 10px;
            font-family: monospace;
            font-size: 13px;
            overflow-x: auto;
            white-space: pre-wrap;
        }
        
        .tags {
            display: flex;
            gap: 5px;
            flex-wrap: wrap;
        }
        
        .tag {
            background: var(--bg-tertiary);
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 12px;
            color: var(--text-secondary);
        }
        
        /* Footer */
        .timeline-footer {
            background: var(--bg-secondary);
            padding: 10px 20px;
            border-top: 1px solid var(--border-color);
        }
        
        .footer-info {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 12px;
            color: var(--text-secondary);
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .timeline-swimlanes {
                width: 120px;
            }
            
            .timeline-events {
                left: 120px;
            }
            
            .event-details-panel {
                width: 100%;
                right: -100%;
            }
            
            .filter-controls {
                flex-direction: column;
                align-items: stretch;
            }
            
            .filter-group {
                width: 100%;
            }
        }
        
        /* Hidden class */
        .hidden {
            display: none !important;
        }
        
        /* Zoom levels */
        .timeline-events.zoom-2x {
            transform: scaleX(2);
            transform-origin: left;
        }
        
        .timeline-events.zoom-4x {
            transform: scaleX(4);
            transform-origin: left;
        }
        
        .timeline-events.zoom-8x {
            transform: scaleX(8);
            transform-origin: left;
        }
    </style>
        """