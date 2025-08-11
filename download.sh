#!/bin/sh
set -eu #x
# depends on htmlq: https://github.com/mgdm/htmlq
# depends on ifne: https://manpages.debian.org/bookworm/moreutils/
# depends on tor: https://manpages.debian.org/bookworm/tor/

download() {
  book_name="$1"
  book_id="$2"
  chapter_id="$(echo $book_id | cut -d/ -f2)"
  curl "https://www.101weiqi.com/book$book_id" --silent |\
        htmlq --text "div.timus.card-wrapper span span" |\
        while read -r problem_id; do
    json="problems/$book_name/$chapter_id/$problem_id.json"
    mkdir -p "$(dirname "$json")"
    if test -f "problems/$book_name/$problem_id.json"; then
        mv "problems/$book_name/$problem_id.json" "$json"
    fi
    while test ! -f "$json"; do
        echo "downloading '$json'"
        curl --proxy "socks5h://localhost:9050" "https://www.101weiqi.com/q/$problem_id/" --silent |\
            grep -oP '^var qqdata = \K.*(?=;$)' |\
            ifne tee "$json" >/dev/null
        if test ! -f "$json"; then
            echo "picking new exit node"
            sudo systemctl reload tor
        fi
    done
done
}

download go-seigen /1220/2585/?page=1
download go-seigen /1220/2585/?page=2
download go-seigen /1220/2585/?page=3
download go-seigen /1220/2585/?page=4
download go-seigen /1221/2586/
download go-seigen /1221/2587/
download go-seigen /1221/2588/
download go-seigen /1221/2589/
download go-seigen /1221/2597/
download go-seigen /1225/2594/
download go-seigen /1225/2595/
download go-seigen /1225/2596/
download go-seigen /1222/2590/?page=1
download go-seigen /1223/2591/?page=1
download go-seigen /1222/2590/?page=2
download go-seigen /1224/2592/?page=1
download go-seigen /1224/2593/?page=1
download go-seigen /1224/2592/?page=2
download go-seigen /1224/2593/?page=2
download go-seigen /1223/2591/?page=2
download go-seigen /1222/2590/?page=3
download go-seigen /1223/2591/?page=3
download go-seigen /1222/2590/?page=4
download go-seigen /1223/2591/?page=4
exit 0

download hashimoto-masterpiece-collection /28506/17300/
download hashimoto-masterpiece-collection /28506/17299/
download hashimoto-masterpiece-collection /28506/17301/
download ishida-tesuji /463/138865/?page=1
download ishida-tesuji /463/138865/?page=2
download ishida-tesuji /463/138865/?page=3
download ishida-tesuji /463/138865/?page=4
download ishida-tesuji /463/138865/?page=5
download ishida-tsumego /28487/17252/
download ishida-tsumego /28487/17253/
download ishida-tsumego /28487/17254/
download ohashi-powerup /26342/15628/
download ohashi-powerup /26342/15629/
download ohashi-powerup /26342/15630/
download ohashi-powerup /26342/15631/
download ohashi-powerup /26342/141485/
download btiyfsag /29806/21015/
download btiyfsag /29806/21016/
download btiyfsag /29806/21017/
download btiyfsag /29806/21018/
download btiyfsag /29806/21019/
download btiyfsag /29806/21020/
download capturing-races /28158/16018/
download capturing-races /28158/16019/
download capturing-races /28158/16022/
download capturing-races /28158/16023/
download capturing-races /28158/16024/
download capturing-races /28158/16025/
download common-problems /421/876/
download common-problems /421/12834/
download common-problems /421/877/
download common-problems /421/877/?page=2
download common-problems /421/878/
download common-problems /421/879/
download common-problems /421/880/
download common-problems /421/881/
download common-problems /421/882/
download common-problems /421/883/
download compact-puzzles /28294/16403/
download compact-puzzles /28294/16404/
download compact-puzzles /28294/16405/
download compact-puzzles /28294/16406/
download compact-puzzles /28294/16407/
download igo-hatsuyoron /fayang/587/
download shikatsu-myoki /miaoji/0/
download xuanxuan-qijing /xuanxuanqijin/90/
download xuanxuan-qijing /xuanxuanqijin/91/
download xuanxuan-qijing /xuanxuanqijin/92/
download beautiful-tsumego /27607/14502/
download beautiful-tsumego /27607/14503/
download weiqi-rapid-drill /800ti/0/
download hashimoto-famous-creations /28501/17289/
download showa-tsumego /1274/2709/
download showa-tsumego /1274/2710/
download showa-tsumego /1274/2711/
download fujisawa-classroom /32769/27356/
download fujisawa-classroom /32769/27357/
download kadakatsuji-tsumego /28482/17225/
download kadakatsuji-tsumego /28482/17226/
download kadakatsuji-tsumego /28482/17227/
download kadakatsuji-tsumego /28482/17228/
download kadakatsuji-tsumego /28482/17229/
download kadakatsuji-tsumego /28482/17230/
download kadakatsuji-tsumego /28482/17231/
download kadakatsuji-tsumego /28482/17232/
download kadakatsuji-tsumego /28482/17233/
download kadakatsuji-tsumego /28482/17234/
download kadakatsuji-tsumego /28482/17235/
download kadakatsuji-tsumego /28482/17236/
download guanzi-pu /3659/21376/
download guanzi-pu /3659/21377/
download fighting-escaping /25358/10433/
download fighting-escaping /25358/10434/
download fighting-escaping /25358/10435/
download fighting-escaping /25358/10436/
download fighting-escaping /25358/10437/
download basic-problems /31528/24176/
download basic-problems /31528/24177/
download basic-problems /31528/24178/
download basic-problems /31528/24179/
download basic-problems /31528/24180/
download at-a-glance /29591/20633/
download at-a-glance /29591/20634/
download hitomi-tsumego /29616/20708/
download hitomi-tsumego /29616/20709/
download hitomi-tsumego /29616/20710/
download hitomi-tsumego /29616/20711/
download maeda-tsumego /28492/17267/
download maeda-tsumego /28503/17296/
download maeda-tsumego /28505/17298/
download weiqi-drills-beginner /1356/2902/
download weiqi-drills-beginner /1356/2907/
download weiqi-drills-intermediate /sihuozhongji/658/
download weiqi-drills-intermediate /sihuozhongji/17896/
download weiqi-drills-intermediate /sihuozhongji/17957/
download segoe-tesuji /shoujinchidian/40/
download segoe-tesuji /shoujinchidian/41/
download segoe-tesuji /shoujinchidian/42/
download segoe-tesuji /shoujinchidian/43/
download segoe-tesuji /shoujinchidian/44/
download segoe-tesuji /shoujinchidian/45/
download segoe-tesuji /shoujinchidian/46/
download segoe-tesuji /shoujinchidian/47/
download segoe-tesuji /shoujinchidian/48/
download segoe-tesuji /shoujinchidian/49/
download segoe-tesuji /shoujinchidian/50/
download segoe-tesuji /shoujinchidian/51/
download segoe-tesuji /shoujinchidian/52/
download segoe-tesuji /shoujinchidian/53/
download segoe-tesuji /shoujinchidian/54/
download segoe-tesuji /shoujinchidian/55/
download segoe-tesuji /shoujinchidian/56/
download segoe-tesuji /shoujinchidian/57/
download segoe-tesuji /shoujinchidian/58/
download segoe-tesuji /shoujinchidian/59/
download segoe-tesuji /shoujinchidian/60/
download segoe-tesuji /shoujinchidian/61/
download segoe-tesuji /shoujinchidian/62/
download segoe-tesuji /shoujinchidian/63/
download segoe-tesuji /shoujinchidian/64/
download segoe-tsumego /shihuochidian/1/
download segoe-tsumego /shihuochidian/2/
download segoe-tsumego /shihuochidian/3/
download segoe-tsumego /shihuochidian/4/
download segoe-tsumego /shihuochidian/5/
download segoe-tsumego /shihuochidian/6/
download segoe-tsumego /shihuochidian/7/
download segoe-tsumego /shihuochidian/8/
download segoe-tsumego /shihuochidian/9/
download segoe-tsumego /shihuochidian/10/
download segoe-tsumego /shihuochidian/11/
download segoe-tsumego /shihuochidian/12/
download segoe-tsumego /shihuochidian/13/
download segoe-tsumego /shihuochidian/14/
download segoe-tsumego /shihuochidian/15/
download segoe-tsumego /shihuochidian/16/
download segoe-tsumego /shihuochidian/17/
download segoe-tsumego /shihuochidian/18/
download segoe-tsumego /shihuochidian/19/
download segoe-tsumego /shihuochidian/20/
download segoe-tsumego /shihuochidian/21/
download segoe-tsumego /shihuochidian/22/
download segoe-tsumego /shihuochidian/23/
download segoe-tsumego /shihuochidian/24/
download segoe-tsumego /shihuochidian/25/
download segoe-tsumego /shihuochidian/26/
download segoe-tsumego /shihuochidian/27/
download segoe-tsumego /shihuochidian/28/
download segoe-tsumego /shihuochidian/29/
download heavenly-dragons /tianlongtu/30/
download heavenly-dragons /tianlongtu/31/
download heavenly-dragons /tianlongtu/32/
download heavenly-dragons /tianlongtu/33/
download heavenly-dragons /tianlongtu/34/
download heavenly-dragons /tianlongtu/35/
download heavenly-dragons /tianlongtu/36/
download heavenly-dragons /tianlongtu/37/
download heavenly-dragons /tianlongtu/38/
download heavenly-dragons /tianlongtu/39/
download leechangho-tesuji /lichanhaoshoujin/721/
download leechangho-tesuji /lichanhaoshoujin/722/
download leechangho-tesuji /lichanhaoshoujin/723/
download leechangho-tesuji /lichanhaoshoujin/724/
download leechangho-tesuji /lichanhaoshoujin/725/
download leechangho-tesuji /lichanhaoshoujin/726/
download leechangho-tesuji /lichanhaoshoujin/727/
download leechangho-tesuji /lichanhaoshoujin/728/
download leechangho-tesuji /lichanhaoshoujin/729/
download leechangho-tesuji /lichanhaoshoujin/730/
download leechangho-tesuji /lichanhaoshoujin/731/
download leechangho-tesuji /lichanhaoshoujin/732/
download leechangho-tesuji /lichanhaoshoujin/733/
download leechangho-tesuji /lichanhaoshoujin/734/
download leechangho-tesuji /lichanhaoshoujin/735/
download leechangho-tesuji /lichanhaoshoujin/736/
download leechangho-tsumego /446/938/
download leechangho-tsumego /446/939/
download leechangho-tsumego /446/940/
download leechangho-tsumego /446/941/
download leechangho-tsumego /446/942/
download leechangho-tsumego /446/943/
download weiqi-1000 /52265/83473/
download weiqi-1000 /52265/83472/
download weiqi-1000 /52265/83471/
download weiqi-1000 /52265/83470/
download weiqi-1000 /52265/83469/
download weiqi-1000 /52265/83468/
download weiqi-1000 /52265/83467/
download weiqi-1000 /52265/83466/
download weiqi-1000 /52265/83465/
download weiqi-1000 /52265/83464/
download weiqi-1000 /52265/83463/
download weiqi-1000 /52265/83462/
download weiqi-1000 /52265/83461/
download weiqi-1000 /52265/83460/
download weiqi-1000 /52265/83459/
download weiqi-1000 /52265/83458/
download weiqi-1000 /52265/83457/
download weiqi-1000 /52265/83456/
download weiqi-1000 /52265/83455/
download weiqi-1000 /52265/83454/
download weiqi-1000 /52265/83453/
download weiqi-1000 /52265/83452/
download weiqi-1000 /52265/83451/
download weiqi-1000 /52265/83450/
download weiqi-1000 /52265/83448/
download leechangho-endgame /29867/0/
download korean-endgame /634/1167/
download korean-endgame /634/1173/
download korean-endgame /634/17885/
download sakata-endgame /894/1772/
download sakata-endgame /894/1773/
download sakata-endgame /894/1774/
download sakata-endgame /894/1775/
download gokyo-seimyo /312/659/
download seedling-project /117/0/
