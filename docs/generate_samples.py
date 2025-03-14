import os
import json
from datetime import datetime

# Create sample data structure
samples = [
    {
        'id': 1,
        'command': 'move mouse to 500, 300',
        'transcription': 'move mouse to 500, 300',
        'interpretation': {
            'type': 'mouse',
            'action': 'move',
            'x': 500,
            'y': 300
        },
        'timestamp': datetime.now().isoformat()
    },
    {
        'id': 2,
        'command': 'click left mouse button',
        'transcription': 'click left mouse button',
        'interpretation': {
            'type': 'mouse',
            'action': 'click',
            'button': 'left'
        },
        'timestamp': datetime.now().isoformat()
    },
    {
        'id': 3,
        'command': 'press control and c',
        'transcription': 'press control and c',
        'interpretation': {
            'type': 'keyboard',
            'action': 'press',
            'keys': ['ctrl', 'c']
        },
        'timestamp': datetime.now().isoformat()
    },
    {
        'id': 4,
        'command': 'type hello world',
        'transcription': 'type hello world',
        'interpretation': {
            'type': 'keyboard',
            'action': 'type',
            'text': 'hello world'
        },
        'timestamp': datetime.now().isoformat()
    },
    {
        'id': 5,
        'command': 'scroll down 5 lines',
        'transcription': 'scroll down 5 lines',
        'interpretation': {
            'type': 'mouse',
            'action': 'scroll',
            'direction': 'down',
            'amount': 5
        },
        'timestamp': datetime.now().isoformat()
    },
    {
        'id': 6,
        'command': 'double click',
        'transcription': 'double click',
        'interpretation': {
            'type': 'mouse',
            'action': 'double_click',
            'button': 'left'
        },
        'timestamp': datetime.now().isoformat()
    },
    {
        'id': 7,
        'command': 'right click',
        'transcription': 'right click',
        'interpretation': {
            'type': 'mouse',
            'action': 'click',
            'button': 'right'
        },
        'timestamp': datetime.now().isoformat()
    },
    {
        'id': 8,
        'command': 'press alt f4',
        'transcription': 'press alt f4',
        'interpretation': {
            'type': 'keyboard',
            'action': 'press',
            'keys': ['alt', 'f4']
        },
        'timestamp': datetime.now().isoformat()
    }
]

# Create directory if it doesn't exist
os.makedirs('docs/github-pages/samples', exist_ok=True)

# Save to JSON file
with open('docs/github-pages/samples/test_samples.json', 'w') as f:
    json.dump(samples, f, indent=2)

print(f'Created sample data with {len(samples)} test cases')
