on run
    -- Get the path to the shell script
    set scriptPath to "/Users/amirshachar/Desktop/Amir/Projects/Personal/swifit/app/debug_helpers/run_get_logs_shortcut.sh"
    
    -- Run the shell script in Terminal
    tell application "Terminal"
        -- Check if Terminal is running
        if not (exists window 1) then
            -- Create a new window if none exists
            do script ""
        end if
        
        -- Run the script in the frontmost window
        do script scriptPath in front window
        activate
    end tell
end run