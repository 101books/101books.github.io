#!/bin/sh
set -eu #x
# depends on htmlq: https://github.com/mgdm/htmlq
# depdens on ifne: https://manpages.debian.org/bookworm/moreutils/

download() {
  book_name="$1"
  book_id="$2"
  curl "https://www.101weiqi.com/book$book_id" --silent | htmlq ".questionitem" --attribute href a | while read -r problem_url; do
    json="problems/$book_name/$(echo "$problem_url" | cut -d/ -f 4-5).json"
    mkdir -p "$(dirname "$json")"
    if test -f "$json"; then
      echo "skipping $json"
    else
      while test ! -f "$json"; do
        sleep 1
        cookie=$(printf "$cookies" | shuf -n1)
        echo "downloading $json using $cookie"
        curl "https://www.101weiqi.com$problem_url" -H "$cookie" --silent |\
          grep -oP 'var g_qq = \K.*(?=;var taskinfo)' |\
          ifne tee "$json" >/dev/null
      done
    fi
  done
}

# throwaway 101weiqi accounts:
# comoti7227@atebin.com
# fimowal358@apn7.com
# mahet70277@bacaki.com
# wojaga4524@calunia.com
# sababib768@cartep.com
# fetayi5707@furnato.com
# rarejik433@apn7.com
cookies="\
cookie: csrftoken=5HcMhB9xblJIiGUKd6GVfblwadZKuKrM55RebC7PeKMTB96myIDevyVS2NVoUGHB; sessionid=f6pjju6hew0k0sjy8c6p5onfi4csjwc6
cookie: csrftoken=xXBhSUvxM4eZ1bNgjy5ZdhBDxafymKsOeGIoORvsNSTftkUgtQ8mHJ9roSHg40p0; sessionid=hkh84n8dsafkrf9ccfywq9ap3x80t8eb
cookie: csrftoken=enlAlnH2H6qCC3JFdjIcQN3CjoFSvUi4J8ZmYtaCfUSPH27MZ6w7xdpNfaPorf9P; sessionid=pl64gvr9ynqs5b3slc2q6h67m1gjp3uu
cookie: csrftoken=ud5PL3nwGU5q3JSh3nSyHT7jraoYoZs2W36M5LTyhAEkpMuCmaVNQdwPwQE817nB; sessionid=mbvxzjo45h3upyojtiiura80zq7okjqo
cookie: csrftoken=sSiFXDmXaqS0qydyiVxFZcN0h2DmftwtmuYZMtC4EvRLX4MjBGpR5weYtnGwVYE5; sessionid=jt0ro3dgfa4tp66xjfewyj9w5xuzlu2x
cookie: csrftoken=smbXsEkBCe15kBHrRkZLH2Gqnbw08qT7lnMifa91JrIoKOBfyMVEa7A55G9tY6Uc; sessionid=8u6ixw392jucq1qvzwfliymv1u0kw9dp"

download seedling-project /c/0/
# https://senseis.xmp.net/?MaedaTsumego
download maeda-tsumego /28492/17267/
download maeda-tsumego /28503/17296/
download maeda-tsumego /28505/17298/
# https://senseis.xmp.net/?WeiqiLifeAndDeathDrills
download weiqi-drills-beginner /1356/2902/
download weiqi-drills-beginner /1356/2907/
# https://senseis.xmp.net/?WeiqiLifeAndDeathDrills
download weiqi-drills-intermediate /sihuozhongji/658/
download weiqi-drills-intermediate /sihuozhongji/17896/
download weiqi-drills-intermediate /sihuozhongji/17957/
# https://senseis.xmp.net/?SegoeTesujiDictionary
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
# https://senseis.xmp.net/?SegoeTsumegoDictionary
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
# https://senseis.xmp.net/?KweonKapyongBadukAcademySeries
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
# https://senseis.xmp.net/?LiChangHoJingjiangWeiqiShoujin
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
# https://senseis.xmp.net/?LiChangHoJingjiangWeiqiSihuo
download leechangho-tsumego /446/938/
download leechangho-tsumego /446/939/
download leechangho-tsumego /446/940/
download leechangho-tsumego /446/941/
download leechangho-tsumego /446/942/
download leechangho-tsumego /446/943/
