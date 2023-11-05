import pandas as pd
import streamlit as st

# データフレームの読み込み
df = pd.read_excel('2023-09_kitei_dataframe.xls')

# DataFrame全体から改行文字を削除
df = df.applymap(lambda x: x.replace('\n', '') if isinstance(x, str) else x)
# DataFrame内の全てのセルに対して半角スペースと全角スペースを削除する関数を適用
df = df.applymap(lambda x: x.replace(' ', '').replace('　', '') if isinstance(x, str) else x)


# Streamlitアプリケーションの設定
st.title('Text Searching App')

# サイドバーに保険種名の選択を追加
selected_insurance_types = st.sidebar.multiselect('保険種名の選択', df['保険種名'].unique())

# サイドバーにキーワードの入力フィールドを追加
keywords_input_container = st.sidebar.empty()
keywords_input = keywords_input_container.text_input('キーワードを入力してください（複数の場合はカンマで区切ってください）')

# クリアボタンを押したかどうかを判定する変数
clear_button_pressed = st.sidebar.button('クリア')

# サイドバーにAND/OR検索のラジオボタンを追加
search_option = st.sidebar.radio('検索オプション', ['AND', 'OR'])

# キーワードが入力された場合に検索を実行
if keywords_input:
    # 複数のキーワードをリストに分割
    keywords_list = [keyword.strip() for keyword in keywords_input.split(',')]

    # AND検索またはOR検索の条件を設定
    if search_option == 'AND':
        condition = all
    else:
        condition = any

    # データフレームから条件に合致する行をフィルタリング
    filtered_df = df[df['本文'].apply(lambda text: condition(keyword in text for keyword in keywords_list))]

    # 保険種名の選択がある場合、それに合致する行をさらにフィルタリング
    if selected_insurance_types:
        filtered_df = filtered_df[filtered_df['保険種名'].isin(selected_insurance_types)]

    # 各規程名ごとのヒット件数をカウント
    regulation_counts = filtered_df['規程名'].value_counts().reset_index()
    regulation_counts.columns = ['規程名', 'ヒット件数']

    # フィルタリングされたデータを表示
    st.write('検索結果:')
    st.write(f"検索結果総数: {len(filtered_df)} 件")
    st.write('各規程名ごとのヒット件数:')
    st.write(regulation_counts)


    for index, row in filtered_df.iterrows():
        with st.expander(f'結果 {index + 1}', expanded=True):  # `expanded=True` でエクスパンダを自動的に開く
            # キーワードを赤字にして全文を表示
            for keyword in keywords_list:
                highlighted_text = row['本文'].replace(keyword, f"<span style='color:red;'>{keyword}</span>")
                st.write(f"**規程名:** {row['規程名']}")
                st.write(f"**括弧書き:** {row['括弧書き']}")
                st.write(f"**条番号:** {row['条番号']}")
                st.write(f"**本文:**")
                st.markdown(highlighted_text, unsafe_allow_html=True)


# クリアボタンがクリックされた場合、一時的に新しいテキスト入力ウィジェットを表示してキーワード入力をクリア
if clear_button_pressed:
    keywords_input_container.empty()
    new_keywords_input = st.sidebar.text_input('キーワードを入力してください（複数の場合はカンマで区切ってください）')
    keywords_input_container.text_input('', value=new_keywords_input)
