import streamlit as st
import random
import time

# -----------------------------
# 기본 설정
# -----------------------------
WIDTH = 10
HEIGHT = 20

SHAPES = {
    "I": [
        [[1, 1, 1, 1]],
    ],
    "O": [
        [[1, 1],
         [1, 1]],
    ],
    "T": [
        [[0, 1, 0],
         [1, 1, 1]],
    ],
    "S": [
        [[0, 1, 1],
         [1, 1, 0]],
    ],
    "Z": [
        [[1, 1, 0],
         [0, 1, 1]],
    ],
    "J": [
        [[1, 0, 0],
         [1, 1, 1]],
    ],
    "L": [
        [[0, 0, 1],
         [1, 1, 1]],
    ],
}

COLORS = {
    "I": "#00FFFF",
    "O": "#FFFF00",
    "T": "#A020F0",
    "S": "#00FF00",
    "Z": "#FF0000",
    "J": "#0000FF",
    "L": "#FFA500",
}


# -----------------------------
# 게임 관련 함수
# -----------------------------
def create_board():
    return [[None for _ in range(WIDTH)] for _ in range(HEIGHT)]


def new_piece():
    shape_name = random.choice(list(SHAPES.keys()))
    shape = [row[:] for row in SHAPES[shape_name][0]]

    return {
        "type": shape_name,
        "shape": shape,
        "x": WIDTH // 2 - len(shape[0]) // 2,
        "y": 0,
    }


def collision(board, piece, dx=0, dy=0, new_shape=None):
    shape = new_shape if new_shape is not None else piece["shape"]

    for row in range(len(shape)):
        for col in range(len(shape[row])):
            if shape[row][col]:
                x = piece["x"] + col + dx
                y = piece["y"] + row + dy

                if x < 0 or x >= WIDTH or y >= HEIGHT:
                    return True

                if y >= 0 and board[y][x] is not None:
                    return True

    return False


def rotate(shape):
    return [
        list(row)
        for row in zip(*shape[::-1])
    ]


def lock_piece(board, piece):
    for row in range(len(piece["shape"])):
        for col in range(len(piece["shape"][row])):
            if piece["shape"][row][col]:
                x = piece["x"] + col
                y = piece["y"] + row

                if 0 <= y < HEIGHT and 0 <= x < WIDTH:
                    board[y][x] = piece["type"]


def clear_lines(board):
    new_board = [
        row for row in board
        if any(cell is None for cell in row)
    ]

    cleared = HEIGHT - len(new_board)

    while len(new_board) < HEIGHT:
        new_board.insert(0, [None for _ in range(WIDTH)])

    return new_board, cleared


def render_board(board, piece):
    display = [row[:] for row in board]

    for row in range(len(piece["shape"])):
        for col in range(len(piece["shape"][row])):
            if piece["shape"][row][col]:
                x = piece["x"] + col
                y = piece["y"] + row

                if 0 <= x < WIDTH and 0 <= y < HEIGHT:
                    display[y][x] = piece["type"]

    html = """
    <style>
        .board {
            display: grid;
            grid-template-columns: repeat(10, 28px);
            grid-template-rows: repeat(20, 28px);
            gap: 2px;
            background: #222;
            padding: 5px;
            width: fit-content;
            border-radius: 5px;
        }

        .cell {
            width: 28px;
            height: 28px;
            background: #111;
            border-radius: 3px;
        }
    """

    for color in COLORS.values():
        html += f"""
        .cell-{color.replace('#', '')} {{
            background: {color};
            box-shadow: inset 0 0 3px #fff;
        }}
        """

    html += "</style><div class='board'>"

    for row in display:
        for cell in row:
            if cell is None:
                html += "<div class='cell'></div>"
            else:
                color = COLORS[cell].replace("#", "")
                html += f"<div class='cell cell-{color}'></div>"

    html += "</div>"

    return html


# -----------------------------
# 게임 초기화
# -----------------------------
def init_game():
    st.session_state.board = create_board()
    st.session_state.current = new_piece()
    st.session_state.next_piece = new_piece()
    st.session_state.score = 0
    st.session_state.lines = 0
    st.session_state.game_over = False


if "board" not in st.session_state:
    init_game()


# -----------------------------
# 화면
# -----------------------------
st.set_page_config(
    page_title="Python Tetris",
    page_icon="🧱",
    layout="centered"
)

st.title("🧱 Python Tetris")
st.caption("Python + Streamlit으로 만든 간단한 테트리스")

col1, col2 = st.columns(2)

with col1:
    st.metric("점수", st.session_state.score)

with col2:
    st.metric("제거한 줄", st.session_state.lines)


# -----------------------------
# 조작 버튼
# -----------------------------
st.subheader("조작")

c1, c2, c3, c4, c5 = st.columns(5)

if c1.button("⬅️"):
    if not collision(st.session_state.board,
                     st.session_state.current,
                     dx=-1):
        st.session_state.current["x"] -= 1

if c2.button("⬇️"):
    if not collision(st.session_state.board,
                     st.session_state.current,
                     dy=1):
        st.session_state.current["y"] += 1

if c3.button("➡️"):
    if not collision(st.session_state.board,
                     st.session_state.current,
                     dx=1):
        st.session_state.current["x"] += 1

if c4.button("🔄"):
    new_shape = rotate(st.session_state.current["shape"])

    if not collision(
        st.session_state.board,
        st.session_state.current,
        new_shape=new_shape
    ):
        st.session_state.current["shape"] = new_shape

if c5.button("⬇️⬇️"):
    while not collision(
        st.session_state.board,
        st.session_state.current,
        dy=1
    ):
        st.session_state.current["y"] += 1


# -----------------------------
# 자동 낙하
# -----------------------------
if not st.session_state.game_over:

    if not collision(
        st.session_state.board,
        st.session_state.current,
        dy=1
    ):
        st.session_state.current["y"] += 1

    else:
        lock_piece(
            st.session_state.board,
            st.session_state.current
        )

        st.session_state.board, cleared = clear_lines(
            st.session_state.board
        )

        if cleared:
            score_table = {
                1: 100,
                2: 300,
                3: 500,
                4: 800
            }

            st.session_state.score += score_table.get(
                cleared, cleared * 200
            )

            st.session_state.lines += cleared

        st.session_state.current = st.session_state.next_piece
        st.session_state.next_piece = new_piece()

        if collision(
            st.session_state.board,
            st.session_state.current
        ):
            st.session_state.game_over = True


# -----------------------------
# 게임 보드 출력
# -----------------------------
st.markdown(
    render_board(
        st.session_state.board,
        st.session_state.current
    ),
    unsafe_allow_html=True
)


# -----------------------------
# 게임 오버
# -----------------------------
if st.session_state.game_over:
    st.error("💥 GAME OVER!")

    if st.button("🔄 다시 시작"):
        init_game()
        st.rerun()


# -----------------------------
# 자동 새로고침
# -----------------------------
if not st.session_state.game_over:
    time.sleep(0.5)
    st.rerun()
