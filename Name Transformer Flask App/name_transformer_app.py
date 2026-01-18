from flask import Flask, request, render_template_string
import random
from collections import Counter

app = Flask(__name__)

# HTML Template with cool styling
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>✨ Name Transformer Pro ✨</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            animation: gradientShift 15s ease infinite;
        }

        @keyframes gradientShift {
            0%, 100% { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
            50% { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
        }

        .container {
            max-width: 900px;
            margin: 40px auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            animation: slideUp 0.5s ease;
        }

        @keyframes slideUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }

        h1 {
            text-align: center;
            color: #667eea;
            margin-bottom: 10px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }

        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-style: italic;
        }

        .result-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            margin: 30px 0;
            text-align: center;
            animation: pulse 0.5s ease;
        }

        @keyframes pulse {
            0% { transform: scale(0.95); }
            50% { transform: scale(1.02); }
            100% { transform: scale(1); }
        }

        .uppercase-name {
            font-size: 3em;
            font-weight: bold;
            letter-spacing: 5px;
            margin: 20px 0;
            text-shadow: 3px 3px 6px rgba(0,0,0,0.2);
        }

        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }

        .feature-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid #667eea;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }

        .feature-title {
            color: #667eea;
            font-weight: bold;
            font-size: 1.1em;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
        }

        .feature-content {
            color: #333;
            font-size: 1.3em;
            font-weight: 600;
        }

        .fun-facts {
            background: #fff3cd;
            border: 2px dashed #ffc107;
            border-radius: 12px;
            padding: 20px;
            margin: 20px 0;
        }

        .fun-facts h3 {
            color: #ff6b6b;
            margin-bottom: 15px;
        }

        .fun-facts ul {
            list-style: none;
            padding: 0;
        }

        .fun-facts li {
            padding: 8px 0;
            color: #555;
            position: relative;
            padding-left: 25px;
        }

        .fun-facts li:before {
            content: "🎯";
            position: absolute;
            left: 0;
        }

        .try-form {
            background: #e9ecef;
            padding: 25px;
            border-radius: 12px;
            margin-top: 30px;
        }

        .try-form h3 {
            color: #667eea;
            margin-bottom: 15px;
        }

        .try-form input {
            width: 70%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 1em;
            margin-right: 10px;
        }

        .try-form button {
            padding: 12px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            cursor: pointer;
            transition: transform 0.2s;
        }

        .try-form button:hover {
            transform: scale(1.05);
        }

        .char-badges {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
            margin: 20px 0;
        }

        .badge {
            background: rgba(255,255,255,0.3);
            padding: 8px 15px;
            border-radius: 20px;
            font-weight: bold;
            animation: fadeIn 0.5s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: scale(0.8); }
            to { opacity: 1; transform: scale(1); }
        }

        .no-name {
            text-align: center;
            color: #666;
            padding: 60px 20px;
        }

        .no-name h2 {
            color: #667eea;
            margin-bottom: 15px;
        }

        .example {
            background: #e3f2fd;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            color: #1976d2;
            font-family: monospace;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>✨ Name Transformer Pro ✨</h1>
        <p class="subtitle">Transform your name with style and discover fun facts!</p>

        {% if name %}
            <div class="result-box">
                <div>Your name in UPPERCASE:</div>
                <div class="uppercase-name">{{ uppercase_name }}</div>
                <div class="char-badges">
                    {% for char in unique_chars %}
                        <span class="badge">{{ char }}</span>
                    {% endfor %}
                </div>
            </div>

            <div class="feature-grid">
                <div class="feature-card">
                    <div class="feature-title">📏 Total Characters</div>
                    <div class="feature-content">{{ stats.total_chars }}</div>
                </div>
                <div class="feature-card">
                    <div class="feature-title">🔤 Total Letters</div>
                    <div class="feature-content">{{ stats.letters_only }}</div>
                </div>
                <div class="feature-card">
                    <div class="feature-title">🎵 Vowels</div>
                    <div class="feature-content">{{ stats.vowels }}</div>
                </div>
                <div class="feature-card">
                    <div class="feature-title">🎸 Consonants</div>
                    <div class="feature-content">{{ stats.consonants }}</div>
                </div>
                <div class="feature-card">
                    <div class="feature-title">📝 Words</div>
                    <div class="feature-content">{{ stats.words }}</div>
                </div>
                <div class="feature-card">
                    <div class="feature-title">🔄 Reversed</div>
                    <div class="feature-content">{{ reversed_name }}</div>
                </div>
            </div>

            <div class="fun-facts">
                <h3>🎉 Fun Facts About "{{ name }}"</h3>
                <ul>
                    {% for fact in fun_facts %}
                        <li>{{ fact }}</li>
                    {% endfor %}
                </ul>
            </div>
        {% else %}
            <div class="no-name">
                <h2>👋 Welcome!</h2>
                <p>Add your name to the URL to see the magic happen!</p>
                <div class="example">
                    <strong>Example:</strong> ?name=YourName
                    <br><br>
                    <strong>Try it:</strong> /?name=Rahul or /?name=Priya
                </div>
            </div>
        {% endif %}

        <div class="try-form">
            <h3>🚀 Try Another Name</h3>
            <form method="GET" action="/">
                <input type="text" name="name" placeholder="Enter a name..." value="{{ name or '' }}" required>
                <button type="submit">Transform!</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

def analyze_name(name):
    """Cool function to analyze name statistics"""
    vowels = sum(1 for char in name.lower() if char in 'aeiou')
    consonants = sum(1 for char in name.lower() if char.isalpha() and char not in 'aeiou')

    return {
        'total_chars': len(name),
        'letters_only': sum(1 for char in name if char.isalpha()),
        'vowels': vowels,
        'consonants': consonants,
        'words': len(name.split())
    }

def generate_fun_facts(name, stats):
    """Generate fun facts about the name"""
    facts = []

    # Character frequency analysis
    char_freq = Counter(name.lower().replace(' ', ''))
    if char_freq:
        most_common = char_freq.most_common(1)[0]
        facts.append(f"The letter '{most_common[0].upper()}' appears most frequently ({most_common[1]} time{'s' if most_common[1] > 1 else ''})!")

    # Vowel to consonant ratio
    if stats['consonants'] > 0:
        ratio = round(stats['vowels'] / stats['consonants'], 2)
        facts.append(f"Your vowel-to-consonant ratio is {ratio}, {'very melodious' if ratio > 0.8 else 'nicely balanced'}!")

    # Name length analysis
    if stats['letters_only'] <= 4:
        facts.append("Short and sweet! Studies show shorter names are easier to remember.")
    elif stats['letters_only'] <= 8:
        facts.append("Perfect length! Your name is memorable and easy to pronounce.")
    else:
        facts.append("Majestic and distinguished! Longer names are often associated with elegance.")

    # ASCII value fun
    ascii_sum = sum(ord(char) for char in name if char.isalpha())
    facts.append(f"The ASCII value sum of your name is {ascii_sum} - that's unique!")

    # Palindrome check
    clean_name = ''.join(name.lower().split())
    if clean_name == clean_name[::-1] and len(clean_name) > 1:
        facts.append("🎊 WOW! Your name is a palindrome - it reads the same forwards and backwards!")

    return facts

@app.route('/')
def index():
    name = request.args.get('name', '').strip()

    if name:
        uppercase_name = name.upper()
        stats = analyze_name(name)
        reversed_name = name[::-1]
        unique_chars = sorted(set(char for char in uppercase_name if char.strip()))
        fun_facts = generate_fun_facts(name, stats)

        return render_template_string(
            HTML_TEMPLATE,
            name=name,
            uppercase_name=uppercase_name,
            stats=stats,
            reversed_name=reversed_name,
            unique_chars=unique_chars,
            fun_facts=fun_facts
        )
    else:
        return render_template_string(HTML_TEMPLATE, name=None)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
