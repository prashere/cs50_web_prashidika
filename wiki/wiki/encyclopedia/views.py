from django.shortcuts import render,redirect
from django.http import HttpResponseNotAllowed
import markdown2
import random

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def md_to_html(md_title):
    """
    Takes the markdown page's title, fetches the content using get_entry() function and
    converts the markdown to html using markdown2.markdown() function and returns the 
    html_content
    """
    md_content = util.get_entry(md_title)
    html_content = markdown2.markdown(md_content)
    return html_content

def check_entry_exists(title):
    """
    Checks if the title is present in the available encyclopedia entries, returns True if
    the entry is found, otherwise False.
    """
    return util.get_entry(title) is not None

def render_page(request,title):
    """
    Renders a new page displaying the contents of the entry if the entry exists, otherwise
    renders a "Page Not Found" page.
    """
    if check_entry_exists(title):
       html_content = md_to_html(title)
       return render(request, "encyclopedia/entry.html",
                      {"title":title,"content":html_content})
    else:
        return render(request, "encyclopedia/notFound.html",
                      {"message":"Page not found !"})
    
def search_result(request):
    """
    If the request method is 'POST', performs a search for the query in the form data.
    If an exact match for the query exists, redirects to the individual entry page.
    If no exact match is found, displays a list of entries that have the query as a 
    substring in another html template.
    """
    if request.method == "POST":
        query = request.POST.get('q')
        if check_entry_exists(query):
            return redirect('entry', title=query)
        else:
            entries = util.list_entries()
            possible_entry = []
            for entry in entries:
                if query.lower() in entry.lower():
                    possible_entry.append(entry)
            return render(request,'encyclopedia/searchResult.html',{'entries':possible_entry})
        
def create_entry_page(request):
    """
    Renders the specified HTML page and returns it.
    """
    return render(request, 'encyclopedia/createEntry.html')

def create_new_entry(request):
    """
    Creates a new entry with the provided title and markdown content. 
    If an entry with same title already exists, the function displays an error message.
    Otherwise, successfully creates the page and redirects the user to the created page.
    """
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        existing_entry = util.get_entry(title)
        if existing_entry is None:
            util.save_entry(title,description)
            html_content = md_to_html(title)
            render(request, "encyclopedia/entry.html",
                      {"title":title,"content":html_content})
            return redirect('entry',title=title)
        else:
            return render(request,'encyclopedia/notFound.html',{'message':"Entry already exists !"})  
        
def edit_entry(request,title):
     """
     Fetches the content of an entry using its title.
     Returns the requested edit page passing the title and content in a dictionary.
     """
     content = util.get_entry(title)
     return render(request,"encyclopedia/editEntry.html",{
         'title':title,
         'content':content
     })
    
def save_entry(request):
    """
    Saves an entry using the title and description
    Redirects to the page of the saved entry.
    """
    if request.method == 'POST':
        title = request.POST['title']
        content = request.POST['description']
        util.save_entry(title,content)
        return redirect('entry',title=title)
    
def random_entry(request):
    """
    Redirects the user to a random entry page from the available entries.
    """
    entry_list = util.list_entries()
    chosen_entry = random.choice(entry_list)
    return redirect('entry',title=chosen_entry)


        
        
   


