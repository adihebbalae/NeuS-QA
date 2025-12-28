#!/bin/bash

export DECORD_EOF_RETRY_MAX=20480
for i in *.mp4; do
    echo "--------------------------------------------"
    echo "Processing: $i"
    
    # 1. Attempt Fast Repair (Re-muxing container)
    if ffmpeg -v error -i "$i" -c copy -map 0 -y "temp_$i" > /dev/null 2>&1; then
        mv "temp_$i" "$i"
        echo "✅ $i: Container fixed."
    else
        echo "⚠️  $i: Fast repair failed. Attempting Deep Repair (Re-encoding)..."
        
        # 2. Attempt Deep Repair (Full re-encode for decord compatibility)
        if ffmpeg -v error -i "$i" -c:v libx264 -preset superfast -crf 23 -c:a copy -y "temp_$i" > /dev/null 2>&1; then
            mv "temp_$i" "$i"
            echo "✅ $i: Re-encoded successfully."
        else
            echo "❌ $i: Failed to repair. File may be severely corrupted."
            rm -f "temp_$i"
        fi
    fi
done
echo "--------------------------------------------"
echo "Done! All videos processed and overwritten."
