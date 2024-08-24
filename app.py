import pandas as pd
import streamlit as st
import requests

# CSVファイルのパスとカラム名
csv_file = 'pokemon_list.csv'
katakana_column = 'katakana_name'

# CSVを読み込む
df = pd.read_csv(csv_file)

# 使用済みポケモン名を管理するためのリストを初期化
if "used_pokemon_names" not in st.session_state:
    st.session_state.used_pokemon_names = []

# やり取りの履歴に使用する記録用のリストを初期化
if "history" not in st.session_state:
    st.session_state.history = []

# 小文字を大文字に変換する関数
def convert_small_to_large(kana):
    small_to_large = str.maketrans('ァィゥェォッャュョ', 'アイウエオツヤユヨ')
    return kana.translate(small_to_large)

# 特殊ケースに対応する関数
def handle_special_cases(kana):
    if kana == 'ニドラン♂':
        return 'ス'
    elif kana == 'ニドラン♀':
        return 'メ'
    elif kana == 'ポリゴン2':
        return 'ツ'
    elif kana == 'ポリゴンZ':
        return 'ト'
    else:
        return kana

# 最後の文字を取得し、特殊ルールを適用する関数
def get_last_char(pokemon_name):
    last_char = pokemon_name[-1]
    
    # 長音の場合、直前の文字を使用
    if last_char == 'ー':
        last_char = pokemon_name[-2]
    
    last_char = handle_special_cases(last_char)
    last_char = convert_small_to_large(last_char)
    
    return last_char

# ゲーム開始時にランダムなポケモン名を取得（「ン」で終わらないポケモンを選ぶ）
def get_random_pokemon():
    while True:
        pokemon = df[katakana_column].sample().values[0]
        if not pokemon.endswith('ン') and pokemon not in st.session_state.used_pokemon_names:
            st.session_state.used_pokemon_names.append(pokemon)
            return pokemon

# 次のポケモン名を探す関数（今回のしりとりではまだ使われていないポケモンのみを選ぶ）
def find_next_pokemon(last_char):
    possible_pokemons = df[df[katakana_column].str.startswith(last_char) & ~df[katakana_column].isin(st.session_state.used_pokemon_names)]
    if not possible_pokemons.empty:
        next_pokemon = possible_pokemons[katakana_column].sample().values[0]
        st.session_state.used_pokemon_names.append(next_pokemon)
        return next_pokemon
    else:
        return None

# ユーザー入力がCSVに存在するか確認する関数
def is_valid_pokemon(pokemon_name):
    return pokemon_name in df[katakana_column].values

# ゲームをリセットする関数
def reset_game(keep_game_started=False):
    st.session_state.current_pokemon = None
    st.session_state.used_pokemon_names = []
    st.session_state.history = []  # 履歴をクリア
    if not keep_game_started:
        st.session_state.game_started = False

# ゲーム状態の初期化
if "game_started" not in st.session_state:
    st.session_state.game_started = False
    st.session_state.current_pokemon = None

# Google FontsからDotGothic16をインポートして適用
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DotGothic16&display=swap');

    .custom-font {
        font-family: 'DotGothic16', sans-serif;
        font-size: 50px;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 画像とテキストを同じ列に配置する
# カラム作成参考https://docs.streamlit.io/develop/api-reference/layout/st.columns
col1, col2 = st.columns([1, 15])  # 1:15 の比率でカラム列を作成
with col1:
    st.image("images/monsterball.jpg", width=80)  # 画像を表示　#自分のローカルファイルに画像を準備
with col2:
    st.markdown('<div class="custom-font">ポケモンしりとりゲーム</div>', unsafe_allow_html=True)  # マークダウン形式で書いたテキストを表示

if not st.session_state.game_started:
    if st.button("はじめる"):
        st.session_state.game_started = True
        st.session_state.current_pokemon = get_random_pokemon()

# ゲーム開始後の画面
if st.session_state.game_started and st.session_state.current_pokemon:
    col1, col2 = st.columns([1, 10], gap="small", vertical_alignment="center")
    with col1:
        st.image("images/satoshi.jpg", width=50)  # 画像を表示 #自分のローカルファイルに画像を準備
    with col2:
        st.write(f"トレーナー: ゆけっ！{st.session_state.current_pokemon}")

    # フォームを作成
    with st.form(key='pokemon_form', clear_on_submit=True):
        last_char = get_last_char(st.session_state.current_pokemon)
        user_input = st.text_input("キミのターン: ", placeholder=f"「{last_char}」からはじまるポケモンのなまえは？")
        submit_button = st.form_submit_button(label="こたえる")

        if submit_button:
            if user_input:
                # 1. 頭文字が正しくしりとりになっているか
                last_char = get_last_char(st.session_state.current_pokemon)
                if not user_input.startswith(last_char):
                    st.write(f"{last_char}からはじまるポケモンをいれてね。")
                
                # 2. 入力したポケモンが存在するか
                elif not is_valid_pokemon(user_input):
                    st.write("そのポケモンはいません。ただしいポケモンのなまえをいれてね。")
                
                # 3. 「ン」で終わらないか
                elif user_input.endswith('ン'):
                    st.write("これは「ン」でおわるポケモンだ。めのまえが まっくらに なった！")
                
                # すべての条件が満たされた場合
                else:
                    st.session_state.history.append((st.session_state.current_pokemon, user_input))
                    st.session_state.current_pokemon = find_next_pokemon(get_last_char(user_input))
                    if st.session_state.current_pokemon:
                        if st.session_state.current_pokemon.endswith('ン'):
                            st.write(f"トレーナー: すまない、{st.session_state.current_pokemon}・・・")
                            st.write("トレーナーが「ン」でおわるポケモンをだしたので、戦闘不能！あなたの勝ち！")
                        else:
                            st.write(f"トレーナー: {st.session_state.current_pokemon}")
                            st.markdown("**※もういちど「こたえる」をおしてね**")
                    else:
                        st.write("トレーナー: ポケモンがみつかりませんでした。あなたの勝ちです！")

    if st.button("やめる"):
        st.session_state.game_started = False
        st.write("またあそんでくれよな！")
        reset_game()
        # 「最初に戻る」ボタンを表示
        if st.button("はじめにもどる"):
            reset_game()

# CSVファイルのidカラムを定義
id_column = 'id'

# カタカナ名からポケモンIDを取得
# get_pokemon_id_from_katakanaという関数に定義
def get_pokemon_id_from_katakana(katakana_name):
    record = df[df[katakana_column] == katakana_name]
    if not record.empty:
        return record[id_column].values[0]
    return None

# ポケモンの画像を表示する関数
def get_pokemon_image(pokemon_name):
    pokemon_id = get_pokemon_id_from_katakana(pokemon_name)
    if pokemon_id:
        url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            image_url = data['sprites']['front_default'] # front_default=正面向いているポケモン画像のURLを取得
            return image_url
        return None

    # これまでのやり取りの履歴を表示
if st.session_state.history:
    st.write("これまでのやりとり:")
    for idx, (pokemon, user) in enumerate(st.session_state.history, 1):
        col1, col2, col3, col4 = st.columns([1, 2, 2, 6], gap="small", vertical_alignment="center")
        with col1:
            st.write(f"{idx * 2 - 1}")  # トレーナーの番号
        with col2:
            st.write("トレーナー")
        with col3:
            pokemon_image_url = get_pokemon_image(pokemon)
            if pokemon_image_url:
                st.image(pokemon_image_url, width=70)  # 画像を表示
        with col4:
            st.write(pokemon)
        # 罫線を引く
        st.markdown("<hr style='margin: 0;'>", unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns([1, 2, 2, 6], gap="small", vertical_alignment="center")
        with col1:
            st.write(f"{idx * 2}")  # 自分の番号
        with col2:
            st.write("キミ")
        with col3:
            user_image_url = get_pokemon_image(user)
            if user_image_url:
                st.image(user_image_url, width=70)  # 画像を表示
        with col4:
            st.write(user)
        # 罫線を引く
        st.markdown("<hr style='margin: 0;'>", unsafe_allow_html=True)


# タブを切り替えて表示する内容を変える
tabs = ["ゲーム開始", "ルール"]
selected_tab = st.sidebar.radio("", tabs)


if selected_tab == "ゲーム開始":
    # ここに既存の"ゲーム開始"のコードを埋め込み
    pass

elif selected_tab == "ルール":
    st.write("""
        **ゲームのルール:**
        
    **勝敗判定**  
    ■以下のいずれかの条件を満たすと勝敗が決定します。  
      - 「ン」で終わるポケモンを答えたとき  
      - 「逃げる」ボタンを押したとき  

    **入力制限**  
      - 全角カタカナのみで入力してください。  
      - 「ン」からは始められません。  
      - 存在しないポケモンを入力した場合、エラーが出ます。  

    **しりとりのつなぎ条件**  
      - 濁音・半濁音はそのままつなげます。  
    ・【例】レックウザ → ザングース  
      - 小文字は大文字に変えてつなげます。  
    ・【例】スナバァ → アーマルド  
      - 長音は1文字前の文字でつなげます。  
    ・【例】ファイヤー → ヤングース  
      - メガ進化・キョダイマックス・ゲンシカイキ・リージョンフォーム(○○のすがた)などは含まれません。  
      - フォルム/すがた/モード/スタイル/もよう/かた/かぞく/フェザー/めん違いも1種類とします。  
      - アンノーン・ミノマダム・ロトム・ネクロズマ・ザシアン・ザマゼンタ・ガチグマも1種類とします。  

    **ゲーム対象外ポケモン**  
      - 以下のポケモンはゲーム対象外となります。  

    ・ニドラン♂  
    ・ニドラン♀  
    ・ポリゴン2  
    ・ポリゴンZ1. ゲーム開始を押すと、ランダムに選ばれた初期のポケモンが表示されます。
        2. ユーザーは表示されたポケモンの名前の最後の文字から始まる新しいポケモンの名前を入力しなければなりません。
        3. すでに使用されたポケモン名は再度使用できません。全てのポケモンが使われた場合、ゲームは終了します。
        4. ゲームをいつでもリセットできます。リセットすると、使用済みのポケモンのリストとゲームの履歴がクリアされます。
    """)

