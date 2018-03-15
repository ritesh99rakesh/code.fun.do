from django.http import HttpResponse
from django.template import loader
# Create your views here.
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import FormView, DetailView, ListView

from .forms import FileForm, QuestionForm
from .models import PdfFile
import subprocess
import shlex

from . import views

def index(request):
    template = loader.get_template('answer_generator/index.html')
    context = {
        'company_name': 'Hunar smart',
    }
    return HttpResponse(template.render(context, request))

class PdfFileView(FormView):
	template_name = 'answer_generator/pdf_file_form.html'
	form_class = FileForm

	def get_success_url(self):
		return ('ask_question')

	def form_valid(self, form):
		Pdf_File = PdfFile(
		file=self.get_form_kwargs().get('files')['file'])
		Pdf_File.save()
		name = str(Pdf_File.file.name)
		print(name)
		self.id = Pdf_File.id
		subprocess.call(shlex.split("python3 ../../pdf/pdfminer.six-master/pdf2txt.py ./media/" + name + " -o ./media/answer_generator_files_txt/comprehension.txt"))
		return HttpResponseRedirect((self.get_success_url()))
		


def ask_question(request):
	print("hello")
	subprocess.call('pwd')
	if request.method == 'POST':
		form = QuestionForm(request.POST)
		if form.is_valid():
			print(form.cleaned_data['question'])
			doc_pointer = open("./media/answer_generator_files_txt/comprehension.txt", "r")
			doc = doc_pointer.read()

			print(type(doc))
			ques = form.cleaned_data['question']
			subprocess.call(shlex.split('''python3 ../../facebookResearch/DrQA/scripts/reader/interactive.py --model "../../facebookResearch/DrQA/scripts/reader/multitask.mdl" --no-cuda --tokenizer 'simple' --document ''' + '''"''' + doc + '''"''' + ''' --question ''' +'''"'''+ ques + '''"'''))
			
			return HttpResponseRedirect('/answer_generator/ask_question')
	else:
		form = QuestionForm()

	return render(request, 'answer_generator/ask_question.html', {'form': form})


