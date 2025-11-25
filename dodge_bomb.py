import os
import random
import sys
import pygame as pg


WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP:(0,-5),
    pg.K_DOWN:(0,5),
    pg.K_LEFT:(-5,0),
    pg.K_RIGHT:(5,0),
}


os.chdir(os.path.dirname(os.path.abspath(__file__)))


def init_bb_imgs() -> tuple[list[pg.Surface],list[int]]:
    bb_imgs = []
    bb_accs = []

    for r in range(1,11):
        bb_img = pg.Surface((20*r, 20*r))
        bb_img.set_colorkey((0,0,0))
        pg.draw.circle(bb_img,(255,0,0),(10*r,10*r),10*r)
        bb_imgs.append(bb_img)
        bb_accs = [a for a in range(1,11)]

    return bb_imgs,bb_accs



def gameover(screen: pg.Surface) -> None:
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


    
def check_bound(rct:pg.Rect)->tuple[bool,bool]:
    """
引数：こうかとんRectか爆弾Rect
戻り値：タプル（横方向判定結果,縦方向判定結果）
画面ないならTrue,画面外ならFalse
"""
    yoko, tate = True,True
    if rct.left < 0 or WIDTH < rct.right: # 横方向のはみだしチェック
        yoko =False
    if rct.top < 0 or HEIGHT < rct.bottom:  # 縦方向のはみだしチェック
        tate = False
    return yoko,tate


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    bb_imgs, bb_accs = init_bb_imgs()
    bb_img = pg.Surface((20,20))  # 空のサーフェイス
    pg.draw.circle(bb_img, (255,0,0),(10,10),10) #  半径10の赤い円の描画
    bb_img.set_colorkey((0,0,0))
    bb_rct = bb_img.get_rect()  # 爆弾rect
    bb_rct.center = random.randint(0,WIDTH), random.randint(0,HEIGHT)
    vx,vy = +2,+2  # 爆弾の横移動、縦移動
    clock = pg.time.Clock()
    tmr = 0


    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
            

        screen.blit(bg_img, [0, 0]) 



        if kk_rct.colliderect(bb_rct):
            gameover(screen)
            return

        # if kk_rct.colliderect(bb_rct):
        #     print("game over")
        #     return
        

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        # if key_lst[pg.K_UP]:
        #     sum_mv[1] -= 5
        # if key_lst[pg.K_DOWN]:
        #     sum_mv[1] += 5
        # if key_lst[pg.K_LEFT]:
        #     sum_mv[0] -= 5
        # if key_lst[pg.K_RIGHT]:
        #     sum_mv[0] += 5
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]  # 横方向の移動量
                sum_mv[1] += mv[1]  # 縦方向の移動量


        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True,True):  # 画面外なら
            kk_rct.move_ip(-sum_mv[0],-sum_mv[1])  # がないなら移動
        screen.blit(kk_img, kk_rct)
        yoko,tate = check_bound(bb_rct)
        if not yoko:
             vx *= -1
        if not tate:
             vy *= -1
        bb_rct.move_ip(vx,vy)
        screen.blit(bb_img, bb_rct)


        # 爆弾拡大・加速
        avx = vx * bb_accs[min(tmr//500, 9)]      # 加速した x速度
        avy = vy * bb_accs[min(tmr//500, 9)]      # 加速した y速度
        bb_img = bb_imgs[min(tmr//500, 9)]        # 拡大した爆弾画像
        # Surface の大きさが変わったら、Rect の幅と高さを書き換える
        bb_rct.width  = bb_img.get_rect().width
        bb_rct.height = bb_img.get_rect().height
        # 移動（加速後の速度で）
        bb_rct.move_ip(avx, avy)
        # 描画
        screen.blit(bb_img, bb_rct)
        # 移動
        bb_rct.move_ip(avx, avy)


        pg.display.update()
        tmr += 1
        clock.tick(50)

        

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
