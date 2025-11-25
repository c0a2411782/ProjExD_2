import os
import random
import sys
import pygame as pg


WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, 5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (5, 0),
}


os.chdir(os.path.dirname(os.path.abspath(__file__)))


def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    戻り値：タプル（1. 爆弾Surfaceのリスト, 2. 爆弾の速度リスト）
    処理内容：
    半径 10～100 の赤い円を描画した爆弾Surfaceを 10 個作成
    各爆弾Surfaceは黒を透過色に設定
    爆弾の速度を 1～10 のリストとして作成
    """
    bb_imgs = []
    bb_accs = []
    for r in range(1, 11):
        bb_img = pg.Surface((20*r, 20*r))
        bb_img.set_colorkey((0, 0, 0))
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        bb_imgs.append(bb_img)
        # bb_accs = [a for a in range(1,11)] # ループ内で毎回作成するのは無駄なので外に出しても良いですが、元のロジックを尊重します
    bb_accs = [a for a in range(1, 11)] # ここで作成
    return bb_imgs, bb_accs


def gameover(screen: pg.Surface) -> None:
    """
    引数：screen（描画対象の Pygame Surface）
    戻り値：なし
    処理内容：
    黒の半透明Surfaceを作成して画面全体に表示
    "Game Over" の文字を画面中央に描画
    泣いているこうかとん画像を左右に配置して描画
    描画後、画面を更新して 5 秒間停止
    """
    # 1. 黒半透明の画面
    black_sfc = pg.Surface((WIDTH, HEIGHT))
    black_sfc.set_alpha(180)
    black_sfc.fill((0, 0, 0))
    # 2. Game Over 文字
    fonto = pg.font.Font(None, 80)
    txt = fonto.render("Game Over", True, (255, 255, 255))
    txt_rct = txt.get_rect(center=(WIDTH/2, HEIGHT/2))
    # 3. 泣いているこうかとん画像（右向き1種類だけ）
    cry = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 1.0)
    # 並べる位置（左右）
    cry_left_rct  = cry.get_rect(center=(WIDTH/2 - 200, HEIGHT/2))
    cry_right_rct = cry.get_rect(center=(WIDTH/2 + 200, HEIGHT/2))
    # 4. 描画
    screen.blit(black_sfc, (0, 0))
    screen.blit(txt, txt_rct)
    screen.blit(cry, cry_left_rct)   # 左も右向き
    screen.blit(cry, cry_right_rct)
    # 5秒停止
    pg.display.update()
    pg.time.wait(5000)


def kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    """
    移動量の合計タプルをキー、回転・反転したこうかとんSurfaceを値とする辞書を返す関数
    """
    # デフォルトの画像（左向き）
    img0 = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    # 右向き（左右反転）
    img = pg.transform.flip(img0, True, False)

    kk_dict = {
        (0, 0): img0,           # 停止時
        (5, 0): img,            # 右
        (5, -5): pg.transform.rotozoom(img, 45, 1.0),   # 右上
        (0, -5): pg.transform.rotozoom(img, 90, 1.0),   # 上
        (5, 5): pg.transform.rotozoom(img, -45, 1.0),   # 右下
        (-5, 0): img0,          # 左
        (-5, -5): pg.transform.rotozoom(img0, -45, 1.0),  # 左上
        (0, 5): pg.transform.rotozoom(img, -90, 1.0),   # 下
        (-5, 5): pg.transform.rotozoom(img0, 45, 1.0),    # 左下
    }
    return kk_dict


def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数：こうかとんRectか爆弾Rect
    戻り値：タプル（横方向判定結果,縦方向判定結果）
    画面ないならTrue,画面外ならFalse
    """
    yoko, tate = True, True
    if rct.left < 0 or WIDTH < rct.right:  # 横方向のはみだしチェック
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom:   # 縦方向のはみだしチェック
        tate = False
    return yoko, tate


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")
    
    # 1. こうかとん画像辞書の準備
    kk_images = kk_imgs()
    # 初期画像の設定
    kk_img = kk_images[(0, 0)]
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    
    bb_imgs, bb_accs = init_bb_imgs()
    
    # 初期爆弾設定（大きさはインデックス0のもの）
    bb_img = bb_imgs[0]
    bb_rct = bb_img.get_rect()
    bb_rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
    
    vx, vy = +2, +2  # 爆弾の基本速度
    clock = pg.time.Clock()
    tmr = 0

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return

        screen.blit(bg_img, [0, 0])

        # ゲームオーバー判定
        if kk_rct.colliderect(bb_rct):
            gameover(screen)
            return

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]  # 横方向の移動量
                sum_mv[1] += mv[1]  # 縦方向の移動量

        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):  # 画面外なら
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])  # 元に戻す

        # 2. 移動方向に応じて画像を変更して描画
        # 辞書から画像を取得（該当なしの場合は (0,0) の画像を使う）
        kk_img = kk_images.get(tuple(sum_mv), kk_images[(0, 0)])
        screen.blit(kk_img, kk_rct)

        # 爆弾の移動・加速処理
        # 経過時間に応じて加速倍率と画像を選択
        idx = min(tmr // 500, 9)
        avx = vx * bb_accs[idx]
        avy = vy * bb_accs[idx]
        bb_img = bb_imgs[idx]
        
        # 爆弾の移動（画面端判定）
        bb_rct.move_ip(avx, avy)
        yoko, tate = check_bound(bb_rct)
        if not yoko:
            vx *= -1  # 基本速度を反転
        if not tate:
            vy *= -1  # 基本速度を反転
            
        # サイズが変わった画像を描画
        screen.blit(bb_img, bb_rct)
        
        # Rectのサイズ更新（当たり判定用）
        bb_rct.width = bb_img.get_rect().width
        bb_rct.height = bb_img.get_rect().height

        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()