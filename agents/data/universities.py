"""
Contains data about Chinese universities and related utility functions.
"""

QS_TOP_20_UNIVERSITIES = {
    # 2024 QS World University Rankings Top 20
    "Massachusetts Institute of Technology", "MIT", "麻省理工",
    "University of Cambridge", "剑桥大学",
    "University of Oxford", "牛津大学",
    "Harvard University", "哈佛大学",
    "Stanford University", "斯坦福大学",
    "Imperial College London", "帝国理工学院",
    "ETH Zurich", "苏黎世联邦理工学院",
    "National University of Singapore", "新加坡国立大学", "NUS",
    "University College London", "UCL", "伦敦大学学院",
    "University of California, Berkeley", "伯克利", "加州大学伯克利分校",
    "University of Chicago", "芝加哥大学",
    "The University of Tokyo", "东京大学",
    "Peking University", "北京大学", "北大",
    "Johns Hopkins University", "约翰霍普金斯大学",
    "Yale University", "耶鲁大学",
    "Nanyang Technological University", "南洋理工大学", "NTU",
    "Princeton University", "普林斯顿大学",
    "Tsinghua University", "清华大学", "清华",
    "The University of Edinburgh", "爱丁堡大学",
    "Swiss Federal Institute of Technology Lausanne", "洛桑联邦理工学院", "EPFL"
}

PROJECT_985_UNIVERSITIES = {
    "北京大学", "清华大学", "中国人民大学", "北京航空航天大学", "北京理工大学",
    "中国农业大学", "北京师范大学", "南开大学", "天津大学", "大连理工大学",
    "吉林大学", "哈尔滨工业大学", "复旦大学", "同济大学", "上海交通大学",
    "华东师范大学", "南京大学", "东南大学", "浙江大学", "中国科学技术大学",
    "厦门大学", "山东大学", "中国海洋大学", "武汉大学", "华中科技大学",
    "湖南大学", "中南大学", "中山大学", "华南理工大学", "四川大学",
    "重庆大学", "西安交通大学", "西北工业大学", "兰州大学", "国防科技大学",
    "电子科技大学", "西北农林科技大学", "中国科学院大学"
}

PROJECT_211_UNIVERSITIES = {
    "北京大学", "清华大学", "中国人民大学", "北京航空航天大学", "北京理工大学",
    "中国农业大学", "北京师范大学", "中央民族大学", "南开大学", "天津大学",
    "大连理工大学", "吉林大学", "哈尔滨工业大学", "复旦大学", "同济大学",
    "上海交通大学", "华东师范大学", "南京大学", "东南大学", "浙江大学",
    "中国科学技术大学", "厦门大学", "山东大学", "中国海洋大学", "武汉大学",
    "华中科技大学", "湖南大学", "中南大学", "中山大学", "华南理工大学",
    "四川大学", "重庆大学", "西安交通大学", "西北工业大学", "兰州大学",
    "东北大学", "郑州大学", "武汉理工大学", "电子科技大学", "江南大学",
    "南京航空航天大学", "南京理工大学", "西北农林科技大学", "中国地质大学",
    "东北师范大学", "河海大学", "中国矿业大学", "北京科技大学", "北京邮电大学",
    "华东理工大学", "南京农业大学", "中国石油大学", "中国地质大学（武汉）",
    "西南交通大学", "太原理工大学", "华中农业大学", "华中师范大学", "中国药科大学",
    "西安电子科技大学", "长安大学", "暨南大学", "华南师范大学", "哈尔滨工程大学",
    "燕山大学", "大连海事大学", "西北大学", "上海大学", "苏州大学",
    "云南大学", "贵州大学", "新疆大学", "石河子大学", "海南大学",
    "宁夏大学", "青海大学", "西藏大学", "第二军医大学", "第四军医大学"
}

def is_211_university(university_name: str) -> bool:
    """
    Check if a university is in the 211 Project list.
    
    Args:
        university_name: Name of the university to check
        
    Returns:
        bool: True if the university is in 211 Project, False otherwise
    """
    # Clean up the university name
    cleaned_name = university_name.strip().replace("大学", "").replace("学院", "")
    
    # Check if any 211 university name contains the cleaned name
    for uni in PROJECT_211_UNIVERSITIES:
        if cleaned_name in uni or uni in university_name:
            return True
    
    return False

def is_985_university(university_name: str) -> bool:
    """
    Check if a university is in the 985 Project list.
    
    Args:
        university_name: Name of the university to check
        
    Returns:
        bool: True if the university is in 985 Project, False otherwise
    """
    # Clean up the university name
    cleaned_name = university_name.strip().replace("大学", "").replace("学院", "")
    
    # Check if any 985 university name contains the cleaned name
    for uni in PROJECT_985_UNIVERSITIES:
        if cleaned_name in uni or uni in university_name:
            return True
    
    return False

def is_qs_top20_university(university_name: str) -> bool:
    """
    Check if a university is in the QS World University Rankings Top 20.
    
    Args:
        university_name: Name of the university to check
        
    Returns:
        bool: True if the university is in QS Top 20, False otherwise
    """
    # Clean up the university name
    cleaned_name = university_name.strip().replace("大学", "").replace("学院", "")
    
    # Check if any QS Top 20 university name contains the cleaned name
    for uni in QS_TOP_20_UNIVERSITIES:
        if cleaned_name.lower() in uni.lower() or uni.lower() in university_name.lower():
            return True
    
    return False 