#!/bin/bash
# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
# $1: DB type
# $2: filename to merge in

set -ex
test $# = 2
test -e "$2"

tmp1=`mktemp -p .`
tmp2=`mktemp -p .`
LOCKFILE="/tmp/segbits_$1.db.lock"
LOCKTIMEOUT=30 # 30s timeout
LOCKID=222

function finish {
    echo "Cleaning up temp files"
    rm -f "$tmp1"
    rm -f "$tmp2"
}
trap finish EXIT

db=$URAY_DATABASE_DIR/$URAY_DATABASE/segbits_$1.db

# if the DB exists acquire a lock
if [ -f $db ]; then
	eval "exec $LOCKID>$LOCKFILE"
	# the lock is automatically released on script exit
	flock --timeout $LOCKTIMEOUT $LOCKID
	if [ ! $? -eq 0 ]; then
		echo "Timeout while waiting for lock"
		finish
		exit 1
	fi
fi

# Check existing DB
if [ -f $db ] ; then
    ${URAY_PARSEDB} --strict "$db"
fi

# Check new DB
${URAY_PARSEDB} --strict "$2"

# Fuzzers verify L/R data is equivilent
# However, expand back to L/R to make downstream tools not depend on this
# in case we later find exceptions

ismask=false
case "$1" in
	clel_l)
		sed < "$2" > "$tmp1" \
			-e 's/^CLE\./CLEL_L./' ;;

	clel_r)
		sed < "$2" > "$tmp1" \
			-e 's/^CLE\./CLEL_R./' ;;

	clem)
		sed < "$2" > "$tmp1" \
			-e 's/^CLE./CLEM./' ;;

	clem_r)
		sed < "$2" > "$tmp1" \
			-e 's/^CLE./CLEM_R./' ;;

	rclk_int_l)
		sed < "$2" > "$tmp1" \
			-e 's/^RCLK_INT./RCLK_INT_L./' ;;

	rclk_int_r)
		sed < "$2" > "$tmp1" \
			-e 's/^RCLK_INT./RCLK_INT_R./' ;;

	rclk_clel_l_l)
		sed < "$2" > "$tmp1" \
			-e 's/^RCLK_CLE./RCLK_CLEL_L_L./' ;;

	rclk_clem_r)
		sed < "$2" > "$tmp1" \
			-e 's/^RCLK_CLE./RCLK_CLEM_R./' ;;

	rclk_clem_l)
		sed < "$2" > "$tmp1" \
			-e 's/^RCLK_CLE./RCLK_CLEM_L./' ;;

	rclk_bram_intf_l)
		sed < "$2" > "$tmp1" \
			-e 's/^RCLK_BRAM_INTF./RCLK_BRAM_INTF_L./' ;;

	rclk_bram_intf_td_l)
		sed < "$2" > "$tmp1" \
			-e 's/^RCLK_BRAM_INTF./RCLK_BRAM_INTF_TD_L./' ;;

	rclk_bram_intf_td_r)
		sed < "$2" > "$tmp1" \
			-e 's/^RCLK_BRAM_INTF./RCLK_BRAM_INTF_TD_R./' ;;

	rclk_dsp_intf_l)
		sed < "$2" > "$tmp1" \
			-e 's/^RCLK_DSP_INTF./RCLK_DSP_INTF_L./' ;;

	rclk_dsp_intf_r)
		sed < "$2" > "$tmp1" \
			-e 's/^RCLK_DSP_INTF./RCLK_DSP_INTF_R./' ;;

	rclk_dsp_intf_clkbuf_l)
		cp "$2" "$tmp1" ;;

	rclk_hdio)
		cp "$2" "$tmp1" ;;

	rclk_ams_cfgio)
		cp "$2" "$tmp1" ;;

	rclk_intf_left_term_alto)
		cp "$2" "$tmp1" ;;

	rclk_xiphy_outer_right)
		cp "$2" "$tmp1" ;;

	cmt_right)
		cp "$2" "$tmp1" ;;

	int)
		cp "$2" "$tmp1" ;;

	int_intf_left_term_pss)
		cp "$2" "$tmp1" ;;

	hpio_right)
		cp "$2" "$tmp1" ;;

	xiphy_byte_right)
		cp "$2" "$tmp1" ;;

	hdio_top_right)
		cp "$2" "$tmp1" ;;

	hdio_bot_right)
		cp "$2" "$tmp1" ;;

	dsp_l)
		sed < "$2" > "$tmp1" -e 's/^DSP\./DSP_L./' ;;
	dsp_r)
		sed < "$2" > "$tmp1" -e 's/^DSP\./DSP_R./' ;;

	bram)
		cp "$2" "$tmp1" ;;

	bram.block_ram)
		cp "$2" "$tmp1" ;;

	bram_l)
		sed < "$2" > "$tmp1" -e 's/^BRAM\./BRAM_L./' ;;
	bram_r)
		sed < "$2" > "$tmp1" -e 's/^BRAM\./BRAM_R./' ;;

	bram_l.block_ram)
		sed < "$2" > "$tmp1" -e 's/^BRAM\./BRAM_L./' ;;
	bram_r.block_ram)
		sed < "$2" > "$tmp1" -e 's/^BRAM\./BRAM_R./' ;;

	*)
		echo "Invalid mode: $1"
		rm -f "$tmp1" "$tmp2"
		exit 1
esac

touch "$db"
if $ismask ; then
    sort -u "$tmp1" "$db" | grep -v '<.*>' > "$tmp2" || true
else
    # tmp1 must be placed second to take precedence over old bad entries
    python3 ${URAY_DIR}/utils/mergedb.py --out "$tmp2" "$db" "$tmp1"
    if ! $ismask ; then
	db_origin=$URAY_DATABASE_DIR/$URAY_DATABASE/segbits_$1.origin_info.db
        if [ ! -f $db_origin ] ; then
            touch "$db_origin"
        fi
        python3 ${URAY_DIR}/utils/mergedb.py --out "$db_origin" "$db_origin" "$tmp1" --track_origin
    fi
fi
# Check aggregate db for consistency and make canonical
${URAY_PARSEDB} --strict "$tmp2" "$db"
