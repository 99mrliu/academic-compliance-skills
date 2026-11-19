#!/usr/bin/env python3
"""scan_pii.py - deterministic scan for sensitive/identifiable information.

Usage: scan_pii.py <paper.txt> <out.json>

Input: pdftotext output with form feeds for page breaks.
Output JSON: {"hit_count": N, "hits": [{"rule": str, "page": int,
  "quote": str, "matched": str, "note": str}]}

Rules are candidate detectors. Every hit must be re-reviewed by the agent
against context (author emails, placeholders, examples are legitimate).
"""
import json
import re
import sys

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
CN_MOBILE_RE = re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?86[- ]?)?0\d{2,3}[- ]?\d{7,8}(?!\d)")
CN_ID_RE = re.compile(r"(?<![0-9A-Za-z])[1-9]\d{5}(?:19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}[0-9Xx](?![0-9A-Za-z])")
IPV4_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
BANK_CARD_RE = re.compile(r"(?<!\d)\d{16,19}(?!\d)")
URL_USER_RE = re.compile(r"https?://[^\s/]*(?:user|u|id)=[^&\s]+", re.I)
DOB_CN_RE = re.compile(r"(?:出生|生日)[^\n]{0,10}(?:19|20)\d{2}\s*年\s*\d{1,2}\s*月\s*\d{1,2}\s*日")
DOB_EN_RE = re.compile(r"(?:date of birth|born on|DOB)[: ]+[^,;\n]{0,30}", re.I)
MRN_CN_RE = re.compile(r"(?:住院号|门诊号|病案号|病历号|就诊卡号)[：: ]?[A-Za-z0-9]{5,15}")
MRN_EN_RE = re.compile(r"\b(?:MRN|medical record (?:no\.?|number)|patient id)[: ]?[A-Za-z0-9-]{5,15}", re.I)
NAME_PATIENT_CN_RE = re.compile(r"患者\s*[张王李赵刘陈杨黄周吴徐孙马朱胡郭何罗高林郑梁谢宋唐许韩冯邓曹彭曾萧田董袁潘蒋蔡余杜叶程苏魏吕丁任卢姚沈钟姜崔谭陆汪范金石廖贾夏韦付方白邹孟熊秦邱江尹薛闫段雷侯龙史陶黎贺顾毛郝龚邵万钱严覃武戴莫孔向汤][一-龥]{1,3}")
TRIAL_REG_RE = re.compile(r"\b(NCT\d{8}|ChiCTR[\w-]{8,}|ISRCTN\d{6,})\b")
CONTROLLED_DB_RE = re.compile(r"\b(dbGaP|EGA[SD]\d{6,}|GEO\s*controlled|controlled[- ]access)\b", re.I)
GENETIC_RE = re.compile(r"人类遗传资源|human genetic resources", re.I)

RULES = [
    ("email", EMAIL_RE, "邮箱地址；排除作者通讯邮箱后复核"),
    ("cn_mobile", CN_MOBILE_RE, "中国大陆手机号样式"),
    ("landline_phone", PHONE_RE, "固定电话样式"),
    ("cn_id_number", CN_ID_RE, "18 位身份证号样式（含出生日期段）"),
    ("ipv4_address", IPV4_RE, "IPv4 地址；排除版本号样式后复核"),
    ("bank_card_like", BANK_CARD_RE, "16-19 位连续数字（银行卡/证件号样式）"),
    ("url_embedded_user", URL_USER_RE, "URL 内嵌用户标识"),
    ("dob_cn", DOB_CN_RE, "精确出生日期（中文）"),
    ("dob_en", DOB_EN_RE, "精确出生日期（英文）"),
    ("mrn_cn", MRN_CN_RE, "病案/住院/门诊号（中文）"),
    ("mrn_en", MRN_EN_RE, "病历号/患者 ID（英文）"),
    ("named_patient_cn", NAME_PATIENT_CN_RE, "患者+姓名组合（中文）"),
    ("trial_registration", TRIAL_REG_RE, "临床试验注册号；通常为合法信息，结合声明核对"),
    ("controlled_access_db", CONTROLLED_DB_RE, "受控访问数据库标记；结合数据可用性声明核对"),
    ("human_genetic_resources", GENETIC_RE, "人类遗传资源标记（受限数据）"),
]


def page_of(text, pos):
    return text.count("\f", 0, pos) + 1


def quote_around(text, start, end, win=100):
    s = max(0, start - win)
    e = min(len(text), end + win)
    return text[s:e].replace("\n", " ").strip()


def main():
    if len(sys.argv) != 3:
        sys.stderr.write("usage: scan_pii.py <paper.txt> <out.json>\n")
        return 2
    try:
        text = open(sys.argv[1], encoding="utf-8", errors="replace").read()
    except OSError as e:
        sys.stderr.write("cannot read input: %s\n" % e)
        return 1
    hits = []
    seen = set()
    for rule, rx, note in RULES:
        for m in rx.finditer(text):
            key = (rule, m.start())
            if key in seen:
                continue
            seen.add(key)
            hits.append({"rule": rule, "page": page_of(text, m.start()),
                         "matched": m.group(0),
                         "quote": quote_around(text, m.start(), m.end()),
                         "note": note})
    hits.sort(key=lambda h: (h["page"], h["rule"]))
    json.dump({"hit_count": len(hits), "hits": hits},
              open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
