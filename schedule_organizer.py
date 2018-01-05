"""
    This program extracts information from testudo.umd.edu,
    the course registration web page for University of Maryland.
    This program scrapes the required course information from the website,
    and chooses classes for the course(which is selected by the user,
     such that the classes do not conflict with one another. The output is
     then stored in a text file.
    NOTE-This program could be made simpler by using UMD's api, however the
    primary purpose of this project is to understand web scraping
"""

from datetime import time
import requests
from bs4 import BeautifulSoup


def get_url(course_id, term_id):
    """
    This method is used to get the url of the web page which contains information
    :param course_id: The name of course the user wants to register(eg:CMSC131)
    :param term_id: The term for which the user wants to register.
    :return:url of website
    """
    url = 'https://ntst.umd.edu/soc/search?courseId='\
          + course_id +\
          '&sectionId=&termId=' \
          + term_id \
          + '&_openSectionsOnly=on&creditCompare=&credits=&courseLevelFilter'\
            '=ALL&instructor=&_facetoface=on&_blended=on&_online=on&courseSta'\
            'rtCompare=&courseStartHour=&courseStartMin=&courseStartAM=&course'\
            'EndHour=&courseEndMin=&courseEndAM=&teachingCenter=ALL&_classDay1'\
            '=on&_classDay2=on&_classDay3=on&_classDay4=on&_classDay5=on'
    return url


def add_dictionaries(d_1, d_2):
    """
    adds 2 dictionaries
    :param d_1: dictionary {'M':List of list of times,'Tu'.....}
    :param d_2: dictionary {'M':List of list of times,'Tu'.....}
    :return: sum of 2 dictionary->dictionary {'M':List of list of times,'Tu'.....}
    """
    final = {}
    for key in d_1:
        if key in d_2:
            if (d_1[key] is None) and (d_2[key] is None):
                final[key] = None
            else:
                if d_1[key] is None:
                    final[key] = d_2[key]
                if d_2[key] is None:
                    final[key] = d_1[key]
                elif d_1[key] is not None and d_2[key] is not None:
                    final[key] = d_2[key] + d_1[key]
    return final


def find_time(string):
    """
    Converts string to time variable
    :param string: of format 12:00:00
    :return: variable of datetime.time(12,0,0)
    """
    t_i_m_e = None
    if '12' in string[0:2]:
        minute = string[3:5]
        t_i_m_e = time(12, int(minute), 0)
        return t_i_m_e
    if 'pm' in string:
        string = string.split('pm')
        string = string[0]
        string = string.split(':')
        hour = int(string[0])
        minute = int(string[1])
        hour += 12
        t_i_m_e = time(hour, minute, 0)
    if 'am' in string:
        string = string.split('am')
        string = string[0]
        string = string.split(':')
        hour = int(string[0])
        minute = int(string[1])
        t_i_m_e = time(hour, minute, 0)
    return t_i_m_e


def get_courses():
    """
    Gets the courses user wants to register
    :return: list of names of courses
    """
    no_courses = int(input('How many courses do you plan to register this semeseter?:'))
    courses = []
    for i in range(no_courses):
        course = input('Please enter course {}:'.format(i + 1))
        course = course.upper()
        courses.append(course)
    return courses


def resolve(days, times, days_times):
    """
    It is a helper method to update the dictionary date_times with values
    :param days:  string in format MTuWThF
    :param times:  its a list of list of times->format([[Start time, End time]])
    :param days_times:dictionary to be updated
    """
    for key in days_times:
        if key in days:
            if days_times[key] is None:
                days_times[key] = [times]
            else:
                days_times[key] = days_times[key] + [times]


def get_course_info(soup, course):
    """
    It returns information of all classes of a course.It divides the
    task of the method get_info
    :param soup: For beautiful soup
    :param course: eg CMSC131
    :return: dictionary of {course+section:Dictionary of days and time}
    """
    mapping = {}
    for info_container in soup.find_all('div', class_='section delivery-f2f'):
        course_and_section = course + ' ' + \
            info_container.find('span', class_='section-id').text.strip()
        days_times = {'M': None, 'Tu': None, 'W': None, 'Th': None, 'F': None}
        class_days_container = info_container.find('div', class_='class-days-container')
        for row in class_days_container.find_all('div', class_='row'):
            days = row.find('span', class_='section-days').text.strip()
            start_time = row.find('span', class_='class-start-time').text.strip()
            end_time = row.find('span', class_='class-end-time').text.strip()
            start_time = find_time(start_time)
            end_time = find_time(end_time)
            t_i_m_e = [start_time, end_time]
            resolve(days, t_i_m_e, days_times)
        mapping[course_and_section] = days_times
    return mapping


def get_info(courses, term_id):
    """
    Gets information of classes of all courses
    :param courses: list of all courses
    :param term_id: the term id for example 201801 for summer 2018
    :return: list of dictionary of format {course+section:Dictionary of days and time}
    """
    all_courses = []
    for course in courses:
        url = get_url(course, term_id)
        source = requests.get(url).text
        soup = BeautifulSoup(source, 'lxml')
        all_courses.append(get_course_info(soup, course))
    return all_courses


def join(dict_1, dict_2):
    """
    Joins 2 dictionaries
    :param dict_1: dictionary->{course+section:Dictionary of days and time}
    :param dict_2: dictionary->{course+section:Dictionary of days and time}
    :return: dictionary->{course+section:Dictionary of days and time}
    """
    d_i_c_t = {}
    for key in dict_1:
        d_i_c_t[key] = dict_1[key]
    for key in dict_2:
        d_i_c_t[key] = dict_2[key]
    return d_i_c_t


def convert_time(t_i_m_e):
    """
    Converts time(12:00)->1200 for easier comparison
    :param t_i_m_e: a time variable
    :return: an int of form 100*hour+minute
    """
    hour = t_i_m_e.hour
    minute = t_i_m_e.minute
    t_i_m_e = hour * 100 + minute
    return t_i_m_e


def time_between(t_i_m_e_1, times):
    """
    Tells if the time is between 2 other times
    :param t_i_m_e_1: a time variable
    :param times: list of 2 time variable [start time,end time]
    :return: true if t_i_m_e1: occurs between other 2 times
    """
    time1 = convert_time(times[0])
    time2 = convert_time(times[1])
    t_i_m_e_1 = convert_time(t_i_m_e_1)
    upper = max(time1, time2)
    lower = min(time1, time2)
    result = False
    if upper >= t_i_m_e_1 >= lower:
        result = True
    return result


def check_conflict(times):
    """
    Checks if there is a time conflict in given times
    :param times: list of list of times
    :return: true if there is a conflict
    """
    if times is None or len(times) == 1:
        return False

    if len(times) == 2:
        conflict = False

        start_time_1 = times[0][0]
        end_time_1 = times[0][1]
        start_time_2 = times[1][0]
        end_time_2 = times[1][1]

        if time_between(start_time_1, times[1]) or time_between(end_time_1, times[1]):
            conflict = True

        if time_between(start_time_2, times[0]) or time_between(end_time_2, times[0]):
            conflict = True

        return conflict

    else:
        conflict = False
        for i in range(0, len(times) - 1):
            for j in range(i + 1, len(times)):
                l_i_s_t = [times[i]] + [times[j]]
                if check_conflict(l_i_s_t):
                    conflict = True
                    break
        return conflict


def works(dictionary):
    """
    Checks whether the classes in dictionary has a time conflict
    :param dictionary: dictionary containing info
    :return: true if there is no time conflict
    """
    d_i_c_t = {'M': None, 'Tu': None, 'W': None, 'Th': None, 'F': None}
    for key in dictionary:
        dictionary = dictionary[key]
        d_i_c_t = add_dictionaries(d_i_c_t, dictionary)

    is_there_conflict = False

    for key in d_i_c_t:
        value = d_i_c_t[key]  # List of list of time
        if check_conflict(value):
            is_there_conflict = True
            break

    return not is_there_conflict


def simplify(lst, num):
    """
    returns all courses without time conflict
    :param lst: list of dictionaries containing info
    :param num: int from 0 to len(lst)-1
    :return: list of dictionaries with courses without time conflict
    """

    # Base case
    l_i_s_t = []
    dictionary = lst[num]

    if num == len(lst) - 1:
        for key in dictionary:
            d_i_c_t = dict()
            d_i_c_t[key] = dictionary[key]
            l_i_s_t.append(d_i_c_t)
        return l_i_s_t

    s_l_i_s_t = simplify(lst, num + 1)
    for item in s_l_i_s_t:  # Dictionary
        for key in dictionary:
            d_i_c_t = dict()
            d_i_c_t[key] = dictionary[key]
            d_i_c_t_final = join(d_i_c_t, item)
            if works(d_i_c_t_final):
                l_i_s_t.append(d_i_c_t_final)
    return l_i_s_t


def main():
    """
    Gets info from the website regarding the courses the
    user wants to register, and outputs the list of classes(one from each course)
    in a text file, all_courses.txt
    """
    term__id = input('Please enter the term id for the semester(eg:201801 for spring 2018):')
    courses = get_courses()
    all_courses = get_info(courses, term__id)
    courses_that_matter = simplify(all_courses, 0)
    real_courses = []
    for i in courses_that_matter:
        out = []
        for key in i:
            out.append(key)
        real_courses.append(out)

    file = open('all_courses.txt', 'w')
    file.write(str(real_courses))


if __name__ == '__main__':
    main()
