import os

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    replacements = {
        'bg-[#090d16] text-white': 'bg-gray-50 text-gray-900',
        'bg-[#0b101d]': 'bg-gray-50',
        'bg-[#070b13]': 'bg-white',
        'bg-gray-900/60': 'bg-white',
        'bg-gray-900/40': 'bg-white',
        'border-white/5': 'border-gray-200',
        'border-white/10': 'border-gray-300',
        'text-gray-400': 'text-gray-500',
        'text-gray-300': 'text-gray-700',
        'text-white': 'text-gray-900',
        'bg-gray-800': 'bg-white border border-gray-200',
        'bg-gray-850': 'bg-white',
        'bg-white/5': 'bg-gray-50',
        'bg-gray-950/60': 'bg-gray-50',
        'text-gradient': 'text-blue-700 font-extrabold',
        'glow-blue': 'shadow-sm',
        'glow-emerald': 'shadow-sm',
        'backdrop-blur': '',
        'bg-emerald-600 text-white rounded-tr-none': 'bg-emerald-600 text-white rounded-tr-none shadow-sm border border-emerald-500',
        'bg-gray-800 text-gray-100 rounded-tl-none border border-white/5': 'bg-white text-gray-900 rounded-tl-none border border-gray-200 shadow-sm'
    }

    for old, new in replacements.items():
        content = content.replace(old, new)

    # Some manual fixes for text legibility in Citizen UI (since chat messages text-gray-100 was changed to text-gray-900)
    content = content.replace('bg-gray-800/80 border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-emerald-500 text-gray-900', 
                              'bg-white border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-emerald-500 text-gray-900 shadow-sm')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

process_file('app/citizen/page.tsx')
print("Citizen UI updated")
