// Standard evidence capture functions for debugging
// Use these as black boxes - they handle all the complexity

const fs = require('fs');
const path = require('path');

async function captureScreenshot(page, name = 'debug-screenshot') {
  const screenshotPath = `${name}.png`;
  await page.screenshot({ path: screenshotPath, fullPage: true });
  console.log(` Screenshot saved: ${screenshotPath}`);
  return screenshotPath;
}

async function scrollAndCapture(page) {
  console.log(' Scrolling through page to capture all content...');
  
  await page.evaluate(() => {
    return new Promise((resolve) => {
      let totalHeight = 0;
      const distance = 100; // pixels to scroll each time
      const delay = 100; // milliseconds between scrolls
      
      const timer = setInterval(() => {
        const scrollHeight = document.body.scrollHeight;
        window.scrollBy(0, distance);
        totalHeight += distance;
        
        if(totalHeight >= scrollHeight - window.innerHeight){
          clearInterval(timer);
          // Pause at bottom to show footer/end of content
          setTimeout(() => {
            // Scroll back to top to show header again
            window.scrollTo(0, 0);
            setTimeout(resolve, 1000); // Pause at top
          }, 2000);
        }
      }, delay);
    });
  });
}

async function finalizeVideo(testName) {
  const videosDir = 'tests/integration/videos/';
  
  // Find the most recently created video
  const files = fs.readdirSync(videosDir);
  const videoFiles = files.filter(f => f.endsWith('.webm'));
  
  let newestVideo = null;
  let newestTime = 0;
  for (const file of videoFiles) {
    const stats = fs.statSync(path.join(videosDir, file));
    if (stats.mtimeMs > newestTime) {
      newestTime = stats.mtimeMs;
      newestVideo = file;
    }
  }
  
  if (!newestVideo) {
    console.error(' No video file found!');
    return null;
  }
  
  // Rename the video to match test name
  const oldPath = path.join(videosDir, newestVideo);
  const newPath = path.join(videosDir, `${testName}.webm`);
  fs.renameSync(oldPath, newPath);
  
  console.log(` Video recording renamed: ${newPath}`);
  return path.resolve(newPath);
}

async function openVideo(videoPath) {
  const { exec } = require('child_process');
  exec(`open "${videoPath}"`, (error) => {
    if (!error) console.log(' Opening video for verification...');
    else console.error('Failed to open video:', error);
  });
}

async function captureCompleteEvidence(page, context, testName) {
  // 1. Scroll through entire page
  await scrollAndCapture(page);
  
  // 2. Take final screenshot
  const screenshotPath = await captureScreenshot(page, `tests/integration/videos/${testName}_final`);
  
  // 3. Close context to save video
  await context.close();
  
  // 4. Process and rename video
  const videoPath = await finalizeVideo(testName);
  
  return { screenshotPath, videoPath };
}

module.exports = { 
  captureScreenshot, 
  scrollAndCapture, 
  finalizeVideo, 
  openVideo,
  captureCompleteEvidence 
};