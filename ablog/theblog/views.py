from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, Category, Comment
from .forms import PostForm, UpdateForm, CommentForm
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect

class HomeView(ListView):
   model = Post
   template_name = 'home.html'
   ordering = ['-post_date']

class ArticleDetailView(DetailView):
   model = Post
   template_name = 'article_details.html'

   def get_context_data(self,*args, **kwargs):
      context=super(ArticleDetailView,self).get_context_data(*args, **kwargs)

      stuff= get_object_or_404(Post,id=self.kwargs['pk'])
      total_likes = stuff.total_likes()

      liked = False
      if stuff.likes.filter(id=self.request.user.id).exists():
         liked = True


      context["total_likes"] = total_likes
      context["liked"] = liked
      return context

class AddPostView(CreateView):
   model = Post
   form_class = PostForm
   template_name = 'add_post.html'

   #if user edits html value
   def post(self, request, **kwargs):
      request.POST = request.POST.copy()
      request.POST['author'] = request.user.id
      return super(AddPostView, self).post(request, **kwargs)

class AddCategoryView(CreateView):
   model = Category
   template_name = 'add_category.html'
   fields = '__all__'

class UpdatePostView(UpdateView):
   model = Post
   form_class = UpdateForm
   template_name = 'update_post.html'

class DeletePostView(DeleteView):
   model = Post
   template_name = 'delete_post.html'
   success_url = reverse_lazy('home')

def CategoryView(request,cats):
   category_posts = Post.objects.filter(category=cats.replace('-',' '))
   return render(request, 'categories.html', {'cats':cats.title().replace('-',' '), 'category_posts': category_posts})

def LikeView(request,pk):
   post = get_object_or_404(Post,id=request.POST.get('post_id'))
   liked = False
   if post.likes.filter(id=request.user.id).exists():
      post.likes.remove(request.user)
      liked = False
   else:
      post.likes.add(request.user)
      liked = True
   return HttpResponseRedirect(reverse('article-detail', args=[str(pk)]))


class AddCommentView(CreateView):
   model = Comment
   form_class = CommentForm
   template_name = 'add_comment.html'

   def get_success_url(self):
      return reverse_lazy('article-detail', kwargs={'pk': self.kwargs['pk']})

   def form_valid(self, form):
      form.instance.post_id = self.kwargs['pk']
      return super().form_valid(form)