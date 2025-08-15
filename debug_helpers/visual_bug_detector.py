#!/usr/bin/env python3
"""
Visual Bug Detector - Advanced visual verification for UI bugs

This module provides computer vision capabilities for detecting visual bugs
that can't be easily verified through DOM inspection alone.
"""

import cv2
import numpy as np
from PIL import Image
import pytesseract
from typing import List, Tuple, Dict, Optional
import os
import json
from datetime import datetime


class VisualBugDetector:
    """Advanced visual bug detection using computer vision techniques"""
    
    def __init__(self, debug_mode: bool = True):
        self.debug_mode = debug_mode
        self.detection_results = []
        
    def extract_text_from_region(self, image_path: str, region: Tuple[int, int, int, int]) -> str:
        """
        Extract text from a specific region of a screenshot using OCR
        
        Args:
            image_path: Path to the screenshot
            region: Tuple of (x1, y1, x2, y2) coordinates
            
        Returns:
            Extracted text from the region
        """
        try:
            image = Image.open(image_path)
            cropped = image.crop(region)
            
            # Save debug image if in debug mode
            if self.debug_mode:
                debug_path = f"debug_ocr_region_{datetime.now().timestamp()}.png"
                cropped.save(debug_path)
                print(f" Debug: OCR region saved to {debug_path}")
            
            # Extract text using Tesseract
            text = pytesseract.image_to_string(cropped)
            return text.strip()
            
        except Exception as e:
            print(f" OCR Error: {e}")
            return ""
    
    def find_template_in_screenshot(self, screenshot_path: str, template_path: str, 
                                    threshold: float = 0.8) -> List[Dict]:
        """
        Find occurrences of a template image within a screenshot
        
        Args:
            screenshot_path: Path to the screenshot
            template_path: Path to the template image to find
            threshold: Matching threshold (0-1)
            
        Returns:
            List of matches with coordinates and confidence
        """
        try:
            # Read images
            screenshot = cv2.imread(screenshot_path)
            template = cv2.imread(template_path)
            
            if screenshot is None or template is None:
                print(" Could not load images")
                return []
            
            # Convert to grayscale for better matching
            gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            
            # Get template dimensions
            h, w = gray_template.shape
            
            # Perform template matching
            result = cv2.matchTemplate(gray_screenshot, gray_template, cv2.TM_CCOEFF_NORMED)
            
            # Find locations where correlation exceeds threshold
            locations = np.where(result >= threshold)
            
            matches = []
            for pt in zip(*locations[::-1]):
                match = {
                    'x': int(pt[0]),
                    'y': int(pt[1]),
                    'width': w,
                    'height': h,
                    'confidence': float(result[pt[1], pt[0]]),
                    'center': (int(pt[0] + w/2), int(pt[1] + h/2))
                }
                matches.append(match)
                
                # Draw rectangle on debug image
                if self.debug_mode:
                    cv2.rectangle(screenshot, pt, (pt[0] + w, pt[1] + h), (0, 255, 0), 2)
            
            # Save debug image with matches
            if self.debug_mode and matches:
                debug_path = f"debug_template_matches_{datetime.now().timestamp()}.png"
                cv2.imwrite(debug_path, screenshot)
                print(f" Debug: Template matches saved to {debug_path}")
            
            return matches
            
        except Exception as e:
            print(f" Template matching error: {e}")
            return []
    
    def count_color_pixels(self, image_path: str, color_range: Dict[str, Tuple[int, int]]) -> int:
        """
        Count pixels within a specific color range (useful for detecting error states)
        
        Args:
            image_path: Path to the screenshot
            color_range: Dict with color channel ranges, e.g., {'red': (200, 255), 'green': (0, 50), 'blue': (0, 50)}
            
        Returns:
            Number of pixels matching the color criteria
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                return 0
            
            # Create mask for color range
            lower = np.array([
                color_range.get('blue', (0, 255))[0],
                color_range.get('green', (0, 255))[0],
                color_range.get('red', (0, 255))[0]
            ])
            upper = np.array([
                color_range.get('blue', (0, 255))[1],
                color_range.get('green', (0, 255))[1],
                color_range.get('red', (0, 255))[1]
            ])
            
            mask = cv2.inRange(image, lower, upper)
            pixel_count = cv2.countNonZero(mask)
            
            # Save debug mask
            if self.debug_mode:
                debug_path = f"debug_color_mask_{datetime.now().timestamp()}.png"
                cv2.imwrite(debug_path, mask)
                print(f" Debug: Color mask saved to {debug_path}")
            
            return pixel_count
            
        except Exception as e:
            print(f" Color detection error: {e}")
            return 0
    
    def compare_screenshots(self, screenshot1_path: str, screenshot2_path: str) -> float:
        """
        Compare two screenshots and return similarity percentage
        
        Args:
            screenshot1_path: Path to first screenshot
            screenshot2_path: Path to second screenshot
            
        Returns:
            Similarity percentage (0-100)
        """
        try:
            img1 = cv2.imread(screenshot1_path)
            img2 = cv2.imread(screenshot2_path)
            
            if img1 is None or img2 is None:
                return 0.0
            
            # Resize images to same size if needed
            if img1.shape != img2.shape:
                img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
            
            # Convert to grayscale
            gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
            
            # Calculate structural similarity
            score = cv2.matchTemplate(gray1, gray2, cv2.TM_CCOEFF_NORMED)[0, 0]
            similarity = float(score * 100)
            
            # Create difference image for debugging
            if self.debug_mode:
                diff = cv2.absdiff(gray1, gray2)
                debug_path = f"debug_diff_{datetime.now().timestamp()}.png"
                cv2.imwrite(debug_path, diff)
                print(f" Debug: Difference image saved to {debug_path}")
            
            return similarity
            
        except Exception as e:
            print(f" Comparison error: {e}")
            return 0.0
    
    def detect_ui_anomalies(self, screenshot_path: str, expected_patterns: Dict) -> List[Dict]:
        """
        Detect UI anomalies based on expected patterns
        
        Args:
            screenshot_path: Path to screenshot
            expected_patterns: Dict of expected UI patterns (colors, text, elements)
            
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        # Check for unexpected red pixels (common error indicator)
        if 'max_red_pixels' in expected_patterns:
            red_pixels = self.count_color_pixels(screenshot_path, {
                'red': (200, 255),
                'green': (0, 100),
                'blue': (0, 100)
            })
            
            if red_pixels > expected_patterns['max_red_pixels']:
                anomalies.append({
                    'type': 'excessive_red_pixels',
                    'severity': 'high',
                    'details': f"Found {red_pixels} red pixels, expected max {expected_patterns['max_red_pixels']}",
                    'likely_cause': 'Error message or error state indicator'
                })
        
        # Check for expected text presence
        if 'expected_text' in expected_patterns:
            full_text = self.extract_text_from_region(
                screenshot_path, 
                expected_patterns.get('text_region', (0, 0, 9999, 9999))
            )
            
            for text in expected_patterns['expected_text']:
                if text.lower() not in full_text.lower():
                    anomalies.append({
                        'type': 'missing_expected_text',
                        'severity': 'medium',
                        'details': f"Expected text '{text}' not found",
                        'likely_cause': 'UI element missing or not rendered'
                    })
        
        # Check for unexpected text (like error messages)
        if 'unexpected_text' in expected_patterns:
            full_text = self.extract_text_from_region(
                screenshot_path,
                expected_patterns.get('text_region', (0, 0, 9999, 9999))
            )
            
            for text in expected_patterns['unexpected_text']:
                if text.lower() in full_text.lower():
                    anomalies.append({
                        'type': 'unexpected_text_found',
                        'severity': 'high',
                        'details': f"Unexpected text '{text}' found",
                        'likely_cause': 'Error message or unintended UI state'
                    })
        
        return anomalies
    
    def create_bug_report(self, screenshot_path: str, anomalies: List[Dict], 
                          user_description: str) -> Dict:
        """
        Create a comprehensive bug report with visual evidence
        
        Args:
            screenshot_path: Path to bug screenshot
            anomalies: List of detected anomalies
            user_description: User's description of the bug
            
        Returns:
            Bug report dictionary
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'screenshot': screenshot_path,
            'user_description': user_description,
            'anomalies_detected': len(anomalies),
            'anomalies': anomalies,
            'visual_indicators': {
                'has_error_colors': any(a['type'] == 'excessive_red_pixels' for a in anomalies),
                'has_unexpected_text': any(a['type'] == 'unexpected_text_found' for a in anomalies),
                'missing_expected_elements': any(a['type'] == 'missing_expected_text' for a in anomalies)
            },
            'confidence': self._calculate_bug_confidence(anomalies)
        }
        
        # Save report
        report_path = f"bug_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f" Bug report saved to: {report_path}")
        return report
    
    def _calculate_bug_confidence(self, anomalies: List[Dict]) -> float:
        """Calculate confidence that a bug exists based on anomalies"""
        if not anomalies:
            return 0.0
        
        confidence = 0.0
        for anomaly in anomalies:
            if anomaly['severity'] == 'high':
                confidence += 0.4
            elif anomaly['severity'] == 'medium':
                confidence += 0.2
            else:
                confidence += 0.1
        
        return min(confidence, 1.0)


# Example usage for the debug prompt
if __name__ == "__main__":
    detector = VisualBugDetector(debug_mode=True)
    
    # Example: Detect error toast in screenshot
    print(" Visual Bug Detection Example\n")
    
    # Simulate bug detection
    screenshot = "screenshots/bug_example.png"
    
    # Define what we're looking for
    patterns = {
        'max_red_pixels': 1000,  # Error indicators are often red
        'unexpected_text': ['error', 'failed', 'exception'],
        'expected_text': ['Success', 'Complete'],
        'text_region': (0, 0, 1920, 200)  # Top area where toasts appear
    }
    
    # Detect anomalies
    anomalies = detector.detect_ui_anomalies(screenshot, patterns)
    
    # Create bug report
    if anomalies:
        print(" BUG DETECTED!")
        for anomaly in anomalies:
            print(f"  - {anomaly['type']}: {anomaly['details']}")
        
        report = detector.create_bug_report(
            screenshot,
            anomalies,
            "Error toast appears when it shouldn't"
        )
        print(f"\n Bug confidence: {report['confidence']*100:.1f}%")
    else:
        print(" No visual anomalies detected")