// Analysis Script Template
// This template demonstrates the structure for analysis scripts created by the /explore command

(function() {
    'use strict';
    
    // Unique identifier for this analysis
    const ANALYSIS_ID = 'ISSUE_${ISSUE_ID}_${TIMESTAMP}';
    const ISSUE_DESCRIPTION = '${ISSUE_DESCRIPTION}';
    
    console.log(`Starting analysis for: ${ISSUE_DESCRIPTION}`);
    console.log(`Analysis ID: ${ANALYSIS_ID}`);
    
    // Main analysis object to collect all data
    const analysisResults = {
        metadata: {
            analysisId: ANALYSIS_ID,
            issueDescription: ISSUE_DESCRIPTION,
            timestamp: new Date().toISOString(),
            url: window.location.href,
            userAgent: navigator.userAgent
        },
        domAnalysis: {},
        computedStyles: {},
        componentState: {},
        performanceMetrics: {},
        customAnalysis: {},
        errors: []
    };
    
    try {
        // 1. DOM Analysis
        analysisResults.domAnalysis = {
            // Add specific DOM queries based on the issue
            // Example:
            // targetElement: document.querySelector('.target-class'),
            // parentStructure: document.querySelector('.parent').innerHTML,
            // siblingCount: document.querySelectorAll('.sibling').length
        };
        
        // 2. Computed Styles Analysis
        analysisResults.computedStyles = {
            // Add specific style analysis based on the issue
            // Example:
            // targetStyles: window.getComputedStyle(element),
            // layout: {
            //     position: style.position,
            //     display: style.display,
            //     dimensions: element.getBoundingClientRect()
            // }
        };
        
        // 3. Component State Analysis (React specific)
        try {
            // Attempt to access React component state if available
            const reactRoot = document.querySelector('#root')._reactRootContainer;
            if (reactRoot) {
                // Add React-specific analysis
            }
        } catch (e) {
            analysisResults.errors.push({
                phase: 'React Analysis',
                error: e.message
            });
        }
        
        // 4. Custom Analysis (Issue-specific)
        analysisResults.customAnalysis = {
            // Add custom analysis specific to the issue being debugged
        };
        
        // 5. Performance Metrics
        if (window.performance) {
            analysisResults.performanceMetrics = {
                timing: performance.timing,
                navigation: performance.navigation,
                memory: performance.memory
            };
        }
        
    } catch (error) {
        analysisResults.errors.push({
            phase: 'General Analysis',
            error: error.message,
            stack: error.stack
        });
    }
    
    // Create downloadable JSON file
    function downloadResults() {
        const dataStr = JSON.stringify(analysisResults, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        
        link.href = url;
        link.download = `analysis_${ANALYSIS_ID}.json`;
        link.style.display = 'none';
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // Clean up
        setTimeout(() => URL.revokeObjectURL(url), 100);
    }
    
    // Download results automatically
    downloadResults();
    
    // Also log summary to console
    console.log('Analysis complete. Summary:');
    console.log(`- DOM elements analyzed: ${Object.keys(analysisResults.domAnalysis).length}`);
    console.log(`- Styles analyzed: ${Object.keys(analysisResults.computedStyles).length}`);
    console.log(`- Errors encountered: ${analysisResults.errors.length}`);
    console.log('Full results downloaded to:', `analysis_${ANALYSIS_ID}.json`);
    
    // Return results for console inspection
    return analysisResults;
})();