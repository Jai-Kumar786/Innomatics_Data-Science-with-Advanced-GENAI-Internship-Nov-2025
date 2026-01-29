from flask import Flask, render_template, request, jsonify
import re

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test-regex', methods=['POST'])
def test_regex():
    try:
        data = request.json
        pattern = data.get('pattern', '')
        test_string = data.get('test_string', '')
        flags_str = data.get('flags', '')
        
        # Parse flags
        flags = 0
        if 'i' in flags_str:
            flags |= re.IGNORECASE
        if 'm' in flags_str:
            flags |= re.MULTILINE
        if 's' in flags_str:
            flags |= re.DOTALL
        if 'x' in flags_str:
            flags |= re.VERBOSE
        
        # Compile regex
        try:
            regex = re.compile(pattern, flags)
        except re.error as e:
            return jsonify({
                'success': False,
                'error': f'Invalid regex: {str(e)}'
            }), 400
        
        # Find all matches
        matches = []
        for match in regex.finditer(test_string):
            match_info = {
                'full_match': match.group(0),
                'start': match.start(),
                'end': match.end(),
                'groups': match.groups(),
                'named_groups': match.groupdict()
            }
            matches.append(match_info)
        
        # Get match count and overall info
        total_matches = len(matches)
        
        return jsonify({
            'success': True,
            'total_matches': total_matches,
            'matches': matches,
            'pattern': pattern,
            'flags': flags_str
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)