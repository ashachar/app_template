"""Timeline JavaScript Module - Contains all JavaScript for timeline interactivity."""


def generate_javascript() -> str:
    """Generate JavaScript for timeline interactivity."""
    return """
    <script>
        // Timeline Interactive JavaScript
        (function() {
            'use strict';
            
            // State
            let currentZoom = 1;
            let selectedEvent = null;
            let filteredEvents = new Set();
            
            // Elements
            const timelineEvents = document.getElementById('timeline-events');
            const detailsPanel = document.getElementById('event-details-panel');
            const detailsContent = document.getElementById('details-content');
            
            // Initialize
            document.addEventListener('DOMContentLoaded', function() {
                initializeEventHandlers();
                initializeFilters();
                initializeControls();
            });
            
            // Event Handlers
            function initializeEventHandlers() {
                // Event click handler
                document.querySelectorAll('.timeline-event').forEach(event => {
                    event.addEventListener('click', function() {
                        selectEvent(this.dataset.eventId);
                    });
                });
                
                // Close details
                document.getElementById('close-details').addEventListener('click', function() {
                    closeDetails();
                });
                
                // Toggle details panel
                document.getElementById('toggle-details').addEventListener('click', function() {
                    toggleDetails();
                });
            }
            
            // Filters
            function initializeFilters() {
                const moduleFilter = document.getElementById('module-filter');
                const typeFilter = document.getElementById('type-filter');
                const severityFilter = document.getElementById('severity-filter');
                const searchFilter = document.getElementById('search-filter');
                const clearFilters = document.getElementById('clear-filters');
                
                [moduleFilter, typeFilter, severityFilter].forEach(filter => {
                    filter.addEventListener('change', applyFilters);
                });
                
                searchFilter.addEventListener('input', applyFilters);
                
                clearFilters.addEventListener('click', function() {
                    moduleFilter.value = '';
                    typeFilter.value = '';
                    severityFilter.value = '';
                    searchFilter.value = '';
                    applyFilters();
                });
            }
            
            function applyFilters() {
                const module = document.getElementById('module-filter').value;
                const type = document.getElementById('type-filter').value;
                const severity = document.getElementById('severity-filter').value;
                const search = document.getElementById('search-filter').value.toLowerCase();
                
                filteredEvents.clear();
                
                document.querySelectorAll('.timeline-event').forEach(event => {
                    let show = true;
                    
                    if (module && event.dataset.module !== module) show = false;
                    if (type && event.dataset.type !== type) show = false;
                    if (severity && event.dataset.severity !== severity) show = false;
                    
                    if (search && show) {
                        const eventData = eventsData.find(e => e.event_id === event.dataset.eventId);
                        if (eventData) {
                            const searchText = (eventData.title + ' ' + eventData.description).toLowerCase();
                            if (!searchText.includes(search)) show = false;
                        }
                    }
                    
                    event.classList.toggle('hidden', !show);
                    if (!show) filteredEvents.add(event.dataset.eventId);
                });
            }
            
            // Controls
            function initializeControls() {
                // Zoom controls
                document.getElementById('zoom-in').addEventListener('click', function() {
                    zoomIn();
                });
                
                document.getElementById('zoom-out').addEventListener('click', function() {
                    zoomOut();
                });
                
                document.getElementById('zoom-fit').addEventListener('click', function() {
                    zoomFit();
                });
                
                // Export/Share
                document.getElementById('export-timeline').addEventListener('click', function() {
                    exportTimeline();
                });
                
                document.getElementById('share-timeline').addEventListener('click', function() {
                    shareTimeline();
                });
            }
            
            // Zoom functions
            function zoomIn() {
                if (currentZoom < 8) {
                    currentZoom *= 2;
                    applyZoom();
                }
            }
            
            function zoomOut() {
                if (currentZoom > 0.25) {
                    currentZoom /= 2;
                    applyZoom();
                }
            }
            
            function zoomFit() {
                currentZoom = 1;
                applyZoom();
                timelineEvents.scrollLeft = 0;
            }
            
            function applyZoom() {
                timelineEvents.classList.remove('zoom-2x', 'zoom-4x', 'zoom-8x');
                if (currentZoom === 2) timelineEvents.classList.add('zoom-2x');
                else if (currentZoom === 4) timelineEvents.classList.add('zoom-4x');
                else if (currentZoom === 8) timelineEvents.classList.add('zoom-8x');
            }
            
            // Event selection
            function selectEvent(eventId) {
                selectedEvent = eventId;
                
                // Highlight selected event
                document.querySelectorAll('.timeline-event').forEach(e => {
                    e.classList.remove('selected');
                });
                document.getElementById('event-' + eventId).classList.add('selected');
                
                // Show details
                showEventDetails(eventId);
            }
            
            function showEventDetails(eventId) {
                const eventData = eventsData.find(e => e.event_id === eventId);
                if (!eventData) return;
                
                detailsContent.innerHTML = `
                    <div class="event-detail-section">
                        <div class="detail-label">Event Type</div>
                        <div class="detail-value">${eventData.event_type}</div>
                        
                        <div class="detail-label">Title</div>
                        <div class="detail-value">${escapeHtml(eventData.title)}</div>
                        
                        <div class="detail-label">Description</div>
                        <div class="detail-value">${escapeHtml(eventData.description)}</div>
                        
                        <div class="detail-label">Time</div>
                        <div class="detail-value">${formatTimestamp(eventData.timestamp)}</div>
                        
                        ${eventData.duration_ms ? `
                        <div class="detail-label">Duration</div>
                        <div class="detail-value">${formatDuration(eventData.duration_ms)}</div>
                        ` : ''}
                        
                        <div class="detail-label">Module</div>
                        <div class="detail-value">${eventData.module}</div>
                        
                        <div class="detail-label">Severity</div>
                        <div class="detail-value">
                            <span class="tag severity-${eventData.severity}">${eventData.severity}</span>
                        </div>
                        
                        ${eventData.tags && eventData.tags.length > 0 ? `
                        <div class="detail-label">Tags</div>
                        <div class="detail-value">
                            <div class="tags">
                                ${eventData.tags.map(tag => `<span class="tag">${escapeHtml(tag)}</span>`).join('')}
                            </div>
                        </div>
                        ` : ''}
                        
                        ${eventData.file_path ? `
                        <div class="detail-label">File</div>
                        <div class="detail-value">
                            <code>${escapeHtml(eventData.file_path)}${eventData.line_number ? ':' + eventData.line_number : ''}</code>
                        </div>
                        ` : ''}
                        
                        ${eventData.stack_trace ? `
                        <div class="detail-label">Stack Trace</div>
                        <div class="detail-value">
                            <div class="code-block">${escapeHtml(eventData.stack_trace)}</div>
                        </div>
                        ` : ''}
                        
                        ${eventData.details && Object.keys(eventData.details).length > 0 ? `
                        <div class="detail-label">Additional Details</div>
                        <div class="detail-value">
                            <div class="code-block">${JSON.stringify(eventData.details, null, 2)}</div>
                        </div>
                        ` : ''}
                        
                        ${eventData.related_event_ids && eventData.related_event_ids.length > 0 ? `
                        <div class="detail-label">Related Events</div>
                        <div class="detail-value">
                            ${eventData.related_event_ids.map(id => {
                                const related = eventsData.find(e => e.event_id === id);
                                return related ? `<a href="#" onclick="selectEvent('${id}'); return false;">${escapeHtml(related.title)}</a><br>` : '';
                            }).join('')}
                        </div>
                        ` : ''}
                    </div>
                `;
                
                detailsPanel.classList.add('open');
            }
            
            function closeDetails() {
                detailsPanel.classList.remove('open');
                selectedEvent = null;
                document.querySelectorAll('.timeline-event').forEach(e => {
                    e.classList.remove('selected');
                });
            }
            
            function toggleDetails() {
                detailsPanel.classList.toggle('open');
            }
            
            // Export/Share functions
            function exportTimeline() {
                const exportData = {
                    metadata: {
                        title: document.querySelector('h1').textContent,
                        exported_at: new Date().toISOString(),
                        filters: {
                            module: document.getElementById('module-filter').value,
                            type: document.getElementById('type-filter').value,
                            severity: document.getElementById('severity-filter').value,
                            search: document.getElementById('search-filter').value
                        }
                    },
                    timeline_data: timelineData,
                    events: eventsData
                };
                
                const blob = new Blob([JSON.stringify(exportData, null, 2)], {type: 'application/json'});
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `timeline_${new Date().getTime()}.json`;
                a.click();
                URL.revokeObjectURL(url);
            }
            
            function shareTimeline() {
                // Generate shareable URL (in real implementation, would upload to server)
                const shareData = {
                    title: document.querySelector('h1').textContent,
                    events: eventsData.length,
                    duration: formatDuration(timelineData.duration * 1000)
                };
                
                const shareUrl = window.location.href + '#shared-' + btoa(JSON.stringify(shareData)).substr(0, 8);
                
                if (navigator.share) {
                    navigator.share({
                        title: 'Debug Timeline',
                        text: `Debug timeline with ${shareData.events} events over ${shareData.duration}`,
                        url: shareUrl
                    });
                } else {
                    // Copy to clipboard
                    navigator.clipboard.writeText(shareUrl).then(() => {
                        alert('Share link copied to clipboard!');
                    });
                }
            }
            
            // Utility functions
            function escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }
            
            function formatTimestamp(timestamp) {
                return new Date(timestamp * 1000).toLocaleString();
            }
            
            function formatDuration(ms) {
                if (ms < 1000) return ms + 'ms';
                if (ms < 60000) return (ms / 1000).toFixed(1) + 's';
                if (ms < 3600000) return (ms / 60000).toFixed(1) + 'm';
                return (ms / 3600000).toFixed(1) + 'h';
            }
            
            // Make selectEvent global for related events links
            window.selectEvent = selectEvent;
        })();
    </script>
        """