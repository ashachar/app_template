(function() {
  console.log('Starting scrollbar analysis...');
  
  var results = {
    timestamp: new Date().toISOString(),
    scrollableElements: [],
    jobCardsElement: null,
    scrollbarWidth: 0
  };
  
  try {
    var allDivs = document.querySelectorAll('div');
    var scrollableElements = [];
    
    for (var i = 0; i < allDivs.length; i++) {
      var div = allDivs[i];
      var style = window.getComputedStyle(div);
      
      if (style.overflowY === 'auto' || style.overflowY === 'scroll') {
        var isJobCards = false;
        var className = div.className || '';
        
        if (className.indexOf('flex-1') !== -1 && className.indexOf('overflow-y-auto') !== -1) {
          isJobCards = true;
        }
        
        var elementInfo = {
          index: i,
          isJobCards: isJobCards,
          className: className,
          paddingLeft: style.paddingLeft,
          paddingRight: style.paddingRight,
          direction: style.direction,
          clientWidth: div.clientWidth,
          offsetWidth: div.offsetWidth,
          scrollWidth: div.scrollWidth
        };
        
        if (div.children.length > 0) {
          var innerDiv = div.children[0];
          var innerStyle = window.getComputedStyle(innerDiv);
          elementInfo.innerDiv = {
            className: innerDiv.className || '',
            paddingLeft: innerStyle.paddingLeft,
            paddingRight: innerStyle.paddingRight
          };
        }
        
        scrollableElements.push(elementInfo);
        
        if (isJobCards) {
          results.jobCardsElement = elementInfo;
          console.log('Found JobCards element:', elementInfo);
        }
      }
    }
    
    results.scrollableElements = scrollableElements;
    
    var testDiv = document.createElement('div');
    testDiv.style.position = 'absolute';
    testDiv.style.top = '-9999px';
    testDiv.style.width = '100px';
    testDiv.style.height = '100px';
    testDiv.style.overflowY = 'scroll';
    testDiv.innerHTML = '<div style="height: 200px;"></div>';
    document.body.appendChild(testDiv);
    
    results.scrollbarWidth = testDiv.offsetWidth - testDiv.clientWidth;
    document.body.removeChild(testDiv);
    
    console.log('Analysis Results:', results);
    
    var jsonString = JSON.stringify(results, null, 2);
    var blob = new Blob([jsonString], { type: 'application/json' });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = 'scrollbar-analysis.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    console.log('Analysis complete - results downloaded');
    
    return results;
    
  } catch (error) {
    console.error('Analysis failed:', error);
    return { error: error.message };
  }
})();