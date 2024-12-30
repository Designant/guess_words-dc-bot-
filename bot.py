import discord
from discord.ext import commands
import random

intents = discord.Intents.default()
client = commands.Bot(command_prefix="!", intents=intents)

# 遊戲狀態
current_displays = []
current_sentences = []
guess_count = 0  # 新增猜測次數變數

# 從文件中讀取單字庫
def load_words(filename="words.txt"):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"單字庫文件 {filename} 找不到，請確保文件存在！")
        return []

# 開始新遊戲
def start_new_game():
    global current_sentences, current_displays, guess_count
    guess_count = 0  # 重置猜測次數
    words = load_words()  # 讀取單字庫
    if not words:
        words = ["Hello, world!", "Python is fun.", "Discord bot challenge."]
    
    current_sentences = random.sample(words, min(3, len(words)))  # 隨機選取 3 個題目
    current_displays = ["".join("-" if c.isalpha() else c for c in sentence) for sentence in current_sentences]

# 顯示進度
def get_progress():
    return "\n".join([f"題目 {i+1}: {current_displays[i]}" for i in range(len(current_displays))])

# 顯示答案
def reveal_all_answers():
    return "\n".join([f"題目 {i+1}: {current_sentences[i]}" for i in range(len(current_sentences))])

# 猜測處理
def process_guess(guess):
    global current_displays, current_sentences, guess_count
    guess_count += 1  # 增加猜測次數

    if len(guess) == 1 and guess.isalpha():  # 字母猜測
        correct = False
        for i, sentence in enumerate(current_sentences):
            for j, char in enumerate(sentence):
                if char.lower() == guess.lower() and current_displays[i][j] == "-":
                    current_displays[i] = current_displays[i][:j] + char + current_displays[i][j+1:]
                    correct = True
        if correct:
            if current_displays == current_sentences:
                return handle_all_guessed()
            return f"字母 '{guess}' 正確！目前進度：\n{get_progress()}"
        else:
            return f"字母 '{guess}' 不存在！"

    elif len(guess) > 1:  # 句子猜測
        if guess.lower() in [sentence.lower() for sentence in current_sentences]:
            index = [sentence.lower() for sentence in current_sentences].index(guess.lower())
            current_displays[index] = current_sentences[index]
            if current_displays == current_sentences:
                return handle_all_guessed()
            return f"你猜中了題目 {index+1}！目前進度：\n{get_progress()}"
        else:
            return f"句子 '{guess}' 不正確！"
    else:
        return "請輸入有效的猜測！"

# 處理全部猜中的情況
def handle_all_guessed():
    global current_sentences, current_displays, guess_count
    answers = reveal_all_answers()
    response = f"恭喜！你猜中了所有題目！\n答案是：\n{answers}\n"
    response += f"總共猜了 {guess_count} 次。\n"
    # 清空遊戲狀態
    current_sentences = []
    current_displays = []
    guess_count = 0
    return response

# 新遊戲指令
@client.tree.command(name="newgame", description="開始新的遊戲")
async def newgame(interaction: discord.Interaction):
    start_new_game()
    progress = get_progress()
    await interaction.response.send_message(f"新遊戲開始！目前進度：\n{progress}", ephemeral=False)

# 猜測指令
@client.tree.command(name="guess", description="猜字母或句子")
async def guess(interaction: discord.Interaction, guess: str):
    result = process_guess(guess)
    await interaction.response.send_message(result, ephemeral=False)

# 結束遊戲指令
@client.tree.command(name="endgame", description="結束遊戲並公布答案")
async def endgame(interaction: discord.Interaction):
    global guess_count, current_sentences, current_displays
    answers = reveal_all_answers()
    response = f"遊戲結束！所有答案：\n{answers}\n"
    response += f"總共猜了 {guess_count} 次。\n"
    # 清空遊戲狀態
    current_sentences = []
    current_displays = []
    guess_count = 0
    await interaction.response.send_message(response, ephemeral=False)

# 啟動機器人
@client.event
async def on_ready():
    await client.tree.sync()  # 同步指令到伺服器
    print(f"已登入為 {client.user}")

# 啟動
client.run('TOKEN')
