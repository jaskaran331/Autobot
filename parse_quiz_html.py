from bs4 import BeautifulSoup
import re

with open('artifacts/full_quiz_page.html', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

submit_btns = [b for b in soup.find_all('button') if 'Submit Quiz' in b.get_text()]
print('Submit Quiz buttons found:', len(submit_btns))
for b in submit_btns:
    print('Button attributes:', b.attrs)

# Let's inspect the options for question 5
target_text = 'Which actions help marketers successfully re-execute'
match = soup.find(string=re.compile(target_text))
if match:
    print('\nFound Q5 text in parent:', match.parent.name)
    # Trace parents up
    curr = match.parent
    for depth in range(5):
        if curr:
            print(f'Depth {depth}: <{curr.name}> class={curr.get("class")}')
            curr = curr.parent

# Let's check how option cards are structured:
option_text = 'Applying similar targeting and messaging strategies'
opt_match = soup.find(string=re.compile('Applying similar targeting'))
if opt_match:
    print('\nFound option text in parent:', opt_match.parent.name)
    curr = opt_match.parent
    for depth in range(5):
        if curr:
            print(f'Opt Depth {depth}: <{curr.name}> class={curr.get("class")} attrs={curr.attrs}')
            curr = curr.parent
