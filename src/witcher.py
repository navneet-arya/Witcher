import sys
import os
import random
import re
import requests, urwid
import urllib.request
import webbrowser
from urwid.widget import (BOX, FLOW, FIXED)
from queue import Queue
from subprocess import PIPE, Popen
from threading import Thread
from bs4 import BeautifulSoup
from .scroll import Scrollable, ScrollBar
import html



# ANSI colour codes
GREEN = '\033[92m'
GRAY = '\033[90m'
CYAN = '\033[36m'
MAGENTA = '\033[95m'
BLUE = '\033[93m'
RED = '\033[31m'
YELLOW = '\033[33m'
END = '\033[0m'        #default color of consol
UNDERLINE = '\033[4m'
BOLD = '\033[1m'

STACK_URL = "https://stackoverflow.com/"



USER_AGENTS = [
    "Mozilla/5.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Firefox/59",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
]


## Helper Functions ##


def read(pipe, funcs):
	"""Reads and pushes piped output to a shared queue and appropriate lists."""
	for line in iter(pipe.readline, b''):
		for func in funcs:
			func(line.decode("utf-8"))
	pipe.close()


def write(get):
	"""Pulls output from shared queue and prints to terminal."""
	for line in iter(get, None):
		print(line)


def get_language(file_path):
	"""Return the language a file is written in."""
	if file_path.endswith(".py"):
		return "python3"

	elif file_path.endswith(".js"):
		return "node"

	elif file_path.endswith(".rb"):
		return "ruby"

	elif file_path.endswith(".go"):
		return "go run"

	elif file_path.endswith(".c") or file_path.endswith(".cpp"):
		return "gcc"
	else:
		return "Unknown language."

def execute(command):
	"""Executes a given command and clones stdout/err to both variable
	and ther terminal (in real-time). """
	process = Popen(
		command,
		cwd=None,
		shell=False,
		close_fds=True,
		stdout=PIPE,
		stderr=PIPE,
		bufsize=1
		)
	output, errors = [], []
	pipe_queue = Queue()

	stdout_thread = Thread(target=read, args=(process.stdout, [pipe_queue.put, output.append]))
	stderr_thread = Thread(target=read, args=(process.stderr, [pipe_queue.put, errors.append]))

	writer_thread = Thread(target=write, args=(pipe_queue.get,))

	for thread in (stdout_thread, stderr_thread, writer_thread):
		thread.daemon = True
		thread.start()

	process.wait()

	for thread in (stdout_thread, stderr_thread):
		thread.join()

	pipe_queue.put(None)

	output = " ".join(output)
	errors = " ".join(errors)
	# print("My errors",errors)
	return (output, errors)



def print_help():
	""" Prints usage instructions. """
	print("{0}Witcher, v0.0.1 - made by @Navneet arya{1}\n".format(BOLD, END))
	print("Commadn-line tool that automatically searches Stack Overflow and displays results in your terminal when you get a compiler error.")
	print("\n\n{0}Usage:{1} $witcher {2}[file_name]{1}".format(UNDERLINE, END, YELLOW))
	print("\n$python3 {0}test.py{1} => $witcher {0}test.py{1}".format(YELLOW, END))
	print("\nIf you just want to query Stack Overflow, use the -q parameter: $witcher -q {0}What is an array comprehension?{1}\n\n".format(YELLOW, END))


def confirm(question):
	""" Prompts a given questions."""
	valid = {"yes": True, "y":True, "ye" : True,
			"no":False, "n":False, "":True}
	prompt = " [y/n] "

	while True:
		choice = input("{0}{1}{2}{3}{4}: ".format(BOLD, CYAN, question, prompt, END)).lower()
		if choice in valid:
			return valid[choice]

		print("Please respond with yes or no.\n")


def get_bs4_object(url):
	""" Turns a given URL into a BeautifulSoup object."""

	try:
		response = requests.get(url, headers={"User-Agent": random.choice(USER_AGENTS)})
		# print("{0}\nConnected to Stack Overflow{1}\n".format(MAGENTA, END))

	except requests.exceptions.RequestException:
		sys.stdout.write("\n%s%s%s" % (RED, "Witcher was unable to fetch Stack Overflow results. "
			"Please check that you are connected to the internet.\n", END))
		sys.exit(1)

	
	if re.search("\.com/nocaptcha", response.url): # URL is a captcha page
		return None
	else:
		return BeautifulSoup(response.text, "html.parser")


## Main ##

def get_search_results(list_of_questions):
	""" Get the search results."""

	search_results = []
	for each in list_of_questions:
		try:
			if each["accepted_answer_id"]:
				Accepted = "Accepted" 
		except KeyError:
			Accepted = "Not Accepted"
		search_results.append({
			'Title': html.unescape(each['title']),
			'Answer Count': each["answer_count"],
			'Status' : Accepted,
			'URL' : each['link']
			})
	return search_results


def search_stackoverflow(query):
	""" Wrapper function for get_search_results. """
	url = "https://api.stackexchange.com/2.2/search/advanced?pagesize=100&order=desc&sort=relevance&q={0}&site=stackoverflow".format(query)
	response = requests.get(url)
	questions = response.json()
	result_count = len(questions["items"])
	
	if result_count == 0:
		return ( [], True)
	else:
		return (get_search_results(questions["items"]) , False)


# Get Description of any question/answer.
def get_desc(soup):
	""" """
	print(soup)
	desc = []
	code_blocks = [block.get_text() for block in soup.find_all("code")]
	newline = False

	i = 0
	for child in soup.recursiveChildGenerator():
		name = getattr(child, "name", None)
		# print("name: {0}, child: {1}".format(name, child))
		
		if name is None :
			# print(child)
			if child in code_blocks:
				print("adding code")
				if newline:
					desc.append(("code", u"\n{0}".format(code_blocks[i])))
					i += 1
					newline = False
				else:
					desc.append(("code", u"{0}".format(child)))
			else:
				newline = child.endswith('\n')
				desc.append(u"{0}".format(child))
	# print(desc)
	return urwid.Text(desc)


# Get the answer of focused question.
def get_question_and_answers(url, answer_count):
	""" """

	result = {}
	soup = get_bs4_object(url)
	if soup == None:
		result['Error']="Sorry, Stack Overflow blocked our request. Try again in a couple seconds."
		return result
	
	result['title'] = soup.find_all('a', class_="question-hyperlink")[0].get_text()
	result["votes"] = soup.find("div", class_="js-vote-count").get_text() # Vote count
	result["asked"] = soup.find("time", itemprop="dateCreated").get_text() # Created date
	m = soup.find_all("div", class_="grid--cell ws-nowrap mb8")[0].text
	view = re.sub("[ \t\n]+", " ", m).replace("\r", "")
	result["viewed"] = view

	result["question_desc"] = get_desc(soup.find("div", class_="s-prose js-post-body"))
	result["total answer"] = soup.find_all("h2", attrs={"class":"mb0"})[0].span.text
	if answer_count > 0:
		ans = get_desc(soup.find("div", attrs={"id":re.compile(r"answer-*")}).find("div", attrs={"class":re.compile(r"s-prose js-post-body")}))
	else:
		ans = urwid.Text(("no answers", u"\nNo answers for this question."))
	result["answer"] = ans
	# print(result)
	return result


class SelectableText(urwid.Text):
	def selectable(self):
		return True

	def keypress(self, size, key):
		return key


def interleave(a, b):
	result = []
	while a and b:
		result.append(a.pop(0))
		result.append(b.pop(0))

	result.extend(a)
	result.extend(b)

	return result

############
# Terminal #
############

class Terminal(object):
	"""docstring for Terminal"""
	def __init__(self, search_results):
		self.search_results, self.viewing_answers = search_results, False
		self.palette = [
			("title", "light cyan, bold", "default", "standout"),
			("stats", "light green", "default", "standout"),
			("status", "", "dark green", "standout"),
			("menu", "black", "light cyan", "standout"),
			("reveal focus", "black", "light cyan", "standout"),
			("no answers", "light red", "default", "standout"),
			("code", "brown", "default", "standout")
		]
		self.menu = urwid.Text([
			u'\n',
			("menu", u" ENTER "), ("light gray", u" View answers "),
			("menu", u" B "), ("light gray", u" Open browser "),
			("menu", u" Q "), ("light gray", u" Quit "),
			("status", u"  "),  ("default", u" Accepted Answer "),
			])

		results = []
		for each in self.search_results:
			if each["Status"] == 'Accepted':
				attr = urwid.AttrMap(SelectableText(self._stylize_title(each)), "status", "reveal focus")
			else:
				attr = urwid.AttrMap(SelectableText(self._stylize_title(each)), None, "reveal focus")
			results.append(attr)
		# results = list(map(lambda result: urwid.AttrMap(SelectableText(self._stylize_title(result)), None , "reveal focus"), self.search_results))
		self.content_container = urwid.ListBox(urwid.SimpleFocusListWalker(results))
		selection = urwid.LineBox(
								self.content_container, title = "{0} Questions Found".format(len(results)),
								title_align = 'center',
								)
		padding_widget = urwid.Padding(selection, left=0, right=0)


		layout = urwid.Frame(body=padding_widget, footer=self.menu)

		self.main_loop = urwid.MainLoop(layout, self.palette, unhandled_input=self._handle_input)
		self.original_widget = self.main_loop.widget

		self.main_loop.run()


	def _handle_input(self, input):
		if input == "enter": # View Answers
			url, answer_count = self._get_selected_link()

			if url != None:
				self.viewing_answers = True
				answer_result = get_question_and_answers(url, answer_count)
				question_stats = answer_result["votes"] + " Votes | " + answer_result["asked"]+ " asked | "+answer_result["viewed"]
				count =  int(answer_result['total answer']) - 1 if int(answer_result['total answer']) - 1 > 0 else 0
				answer_left = urwid.Text(("no answers", str(count) + " More Answer Left"))
				pile = urwid.Pile(self._stylize_question(answer_result['title'], 
					answer_result["question_desc"], question_stats)+ [urwid.Divider('*')] + interleave([answer_result['answer']], 
						[urwid.Divider('-')]+ [answer_left]))


				padding = ScrollBar(Scrollable(urwid.Padding(pile, left=2, right=2)))
				linebox = urwid.LineBox(padding)

				menu = urwid.Text([
					("menu", u" ENTER "), ("light gray", u" View answers "),
					("menu", u" B "), ("light gray", u" Open browser "),
					("menu", u" Q "), ("light gray", u" Quit "),
				])


				# linebox.base_widget.set_text(("no answers", "Getting answer"))
				# linebox.draw_screen()
				self.main_loop.widget = urwid.Frame(body=urwid.Overlay(linebox, self.content_container, "center", ("relative", 90), "middle", ("relative", 100), 10), footer=menu)
		
		elif input in ('b', 'B'): # Open link
			url, _ = self._get_selected_link()

			if url != None:
				webbrowser.open(url)
		elif input == "esc": # Close window
			if self.viewing_answers:
				self.main_loop.widget = self.original_widget
				self.viewing_answers = False
			else:
				raise urwid.ExitMainLoop()
		elif input in ('q', 'Q'): # Quit
			raise urwid.ExitMainLoop()


	def _get_selected_link(self):
		focus, idx = self.content_container.get_focus()
		title = focus.base_widget.text

		for r in self.search_results:
			if title == self._stylize_title(r):
				return r["URL"], r["Answer Count"]


	def _stylize_title(self, search_result):
		return "{0} ({1} Answers)".format(search_result["Title"], search_result["Answer Count"])



	def _stylize_question(self, title, desc, stats):
		new_title = urwid.Text(("title", u"%s" %title))
		new_stats = urwid.Text(("stats", u"%s\n" %stats))

		return [new_title, desc, new_stats]


def get_error_msg(error, language):
	""" Filter the stack trace from stderr """

	if error == "":
		return None

	elif language == "python3":
		if any(e in error for e in ["KeyboardInterrupt", "SystemExit", "GeneratorExit"]):
			return None
		else:
			return error.split('\n')[-2].strip()

	elif language == "node":
		return error.split('\n')[4][1:]

	elif language == "go run":
		return error.split('\n')[1].split(": ", 1)[1][1:]

	elif language == "ruby":
		error_message = error.split('\n')[0]
		return error_message[error_message.rfind(": ")+2:]

	elif language == "gcc":
		error_msg = error.split('\n')
		error_msg = [each.split(": ")[2] for each in error_msg if "error" in each] 
		return error_msg
	return None



def main():
	if len(sys.argv) == 1 or sys.argv[1].lower() == "-h" or sys.argv[1].lower() == '--help':
		print_help()

	elif sys.argv[1].lower() == "-q" or sys.argv[1].lower() == '--query':
		query = ' '.join(sys.argv[2:])
		print("{0}Connecting to Stack Overflow...{1}".format(GREEN, END))
		search_result, captcha = search_stackoverflow(query)

		if search_result != []:
			if captcha:
				print("{0}Sorry, unable to process your request.{1}".format(GREEN, END))
				return
			Terminal(search_result)
		else:
			print("{0}No stackoverflow results found.{1}".format(RED, END))

	language = get_language(sys.argv[1].lower())
	if language == '':
		print("{0} Sorry, we don't support this file.{1}".format(RED, END))
		return

	file_path = sys.argv[1:]
	output, error = execute([language] + file_path)
	if (output, error) == (None, None):
		return


	if confirm("Search on Stack Overflow?"):
		error_msg = get_error_msg(error, language)
		if language == "gcc":
			if len(error_msg) > 1:
				seq = int(input("{0}Total {1} Error occured, Enter the number for which you want to search: {2}".format(GREEN, len(error_msg), END)))
				error_msg = error_msg[seq-1]
			else:
				error_msg = error_msg[0]

		if error_msg != None:
			query = "{0} {1}".format(language, error_msg)
			print("{0}Getting Stack Overflow results...{1}".format(GREEN, END))
			search_results, captcha = search_stackoverflow(query)

			if search_results != []:
				if captcha:
					print("{0}Sorry, unable to process your request.{1}".format(GREEN, END))
					return
				else:
					Terminal(search_results)
			else:
				print("{0}No stackoverflow results found.{1}".format(RED, END))
		else:
			print("{0} No error detected :\n{1}".format(CYAN, END))
	else:
		return



if __name__ == '__main__':
# 	# url = 'https://stackoverflow.com/questions/35403548/how-to-implement-horizontal-scatter-bar-graph-plot-in-ios'
# 	# get_question_and_answers(url, 0)
	main()