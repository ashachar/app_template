# Translate Terms Command

Translates the provided terms into all supported languages in parallel.

## Usage
```
/translate <term1> <term2> <term3> ...
```

## Description
This command invokes multiple translation-key-expert agents in parallel, one for each supported language, to translate all the provided terms. Each agent will:
1. Search for the translation keys in the locale files
2. Add appropriate translations for the terms
3. Follow gender-neutral language preferences where applicable

## Supported Languages
- Hebrew (he)
- English (en) 
- Spanish (es)
- French (fr)
- Russian (ru)
- Ukrainian (uk)
- Arabic (ar)
- Amharic (am)

## Example
```
/translate auth.login.rememberMe dashboard.stats.totalUsers profile.settings.notifications
```

This will create 8 parallel tasks, one for each language, to translate these three keys.

## Implementation
```javascript
// Parse the terms from the command
const terms = prompt.split(' ').slice(1); // Remove '/translate' prefix

// Supported languages
const languages = ['he', 'en', 'es', 'fr', 'ru', 'uk', 'ar', 'am'];

// Create parallel tasks for each language
const translationTasks = languages.map(lang => ({
  description: `Translate to ${lang}`,
  prompt: `Translate the following keys to ${lang}: ${terms.join(', ')}`,
  subagent_type: 'translation-key-expert'
}));

// Execute all tasks in parallel
await Promise.all(translationTasks.map(task => 
  Task(task.description, task.prompt, task.subagent_type)
));
```