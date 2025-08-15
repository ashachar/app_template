#!/usr/bin/env node

/**
 * Find large code files for refactoring
 * Simple script to identify files that might benefit from refactoring
 */

const fs = require('fs').promises;
const path = require('path');
const { execSync } = require('child_process');

// Get all code files using git ls-files (respects .gitignore)
async function findLargeFiles() {
  try {
    // Use git to get all tracked files
    const gitFiles = execSync('git ls-files', { encoding: 'utf-8' })
      .split('\n')
      .filter(Boolean);
    
    // Filter for code files
    const codeExtensions = ['.js', '.jsx', '.ts', '.tsx', '.py', '.java', '.go', '.rb', '.php', '.cs', '.cpp', '.c', '.h', '.swift', '.kt', '.rs'];
    const codeFiles = gitFiles.filter(file => {
      const ext = path.extname(file).toLowerCase();
      return codeExtensions.includes(ext) && 
             !file.includes('node_modules') &&
             !file.includes('.min.') &&
             !file.includes('.d.ts') &&
             !file.includes('dist/') &&
             !file.includes('build/');
    });
    
    // Get line counts for each file
    const fileStats = await Promise.all(
      codeFiles.map(async (file) => {
        try {
          const content = await fs.readFile(file, 'utf-8');
          const lines = content.split('\n').length;
          return { file, lines };
        } catch (err) {
          return null;
        }
      })
    );
    
    // Filter out nulls and files with less than 100 lines
    const validFiles = fileStats
      .filter(stat => stat && stat.lines >= 100)
      .sort((a, b) => b.lines - a.lines)
      .slice(0, 10);
    
    return validFiles;
  } catch (error) {
    console.error('Error finding files:', error);
    return [];
  }
}

// Run if called directly
if (require.main === module) {
  findLargeFiles().then(files => {
    console.log('Top 10 refactoring candidates:\n');
    files.forEach((file, index) => {
      console.log(`${index + 1}. ${file.file} (${file.lines} lines)`);
    });
  });
}

module.exports = { findLargeFiles };