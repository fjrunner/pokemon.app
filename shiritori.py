import requests
import json
import random
import streamlit as st

# 全てのポケモンの名前を取得する
def get_all_pokemon_names():
    response = requests.get("https://pokeapi.co/api/v2/pokemon?limit=1000")
    data = json.loads(response.text)

    return [res["name"] for res in data["results"]]


# 入力されたポケモンの日本語名を取得する
def get_pokemon_japanese_name(name):
    response = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{name}")

    if response.status_code != 200:
        return None

    data = json.loads(response.text)

    for n in data["names"]:
        if n["language"]["name"] == "ja-Hrkt":
            return n["name"]
    
    return None

def main():
    all_pokemon_names = get_all_pokemon_names()

    if 'used_names' not in st.session_state:
        st.session_state.used_names = set()
    if 'current_pokemon' not in st.session_state or st.session_state.current_pokemon == '':
        st.session_state.current_pokemon = random.choice(all_pokemon_names)
        st.session_state.used_names.add(st.session_state.current_pokemon)

    st.title("ポケモンしりとり")
    st.write(f"現在のポケモン：「{get_pokemon_japanese_name(st.session_state.current_pokemon)}」")

    new_pokemon_name = st.text_input("新しいポケモンの名前を入力してください")

    if new_pokemon_name in st.session_state.used_names:
        st.write("そのポケモンはすでに使われました！")
    elif new_pokemon_name:
        english_name = new_pokemon_name.lower()

        japanese_name = get_pokemon_japanese_name(english_name)

        if japanese_name is None:
            st.write("そのポケモンは存在しません！")
        elif japanese_name[0] != get_pokemon_japanese_name(st.session_state.current_pokemon)[-1]:
            st.write("しりとりが成立していません！")
        else:
            st.write(f"ユーザの番：「{japanese_name}」")
            st.session_state.used_names.add(new_pokemon_name)

            # 続きのポケモンを探す
            for name in all_pokemon_names:
                if name in st.session_state.used_names:  # すでに使われている名前はスキップします
                    continue
                
                next_japanese_name = get_pokemon_japanese_name(name)
                if next_japanese_name and next_japanese_name[0] == japanese_name[-1]:
                    st.session_state.used_names.add(name)
                    st.session_state.current_pokemon = name
                    break


if __name__ == "__main__":
    main()