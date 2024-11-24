from django.shortcuts import render, redirect, HttpResponse
from social_app.models import *
import qrcode
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
import json

def root(request):
    return redirect('home')

def about_us(request):
    return render(request, 'about_us.html')

def home(request):
    if not 'user_id' in request.session:
        messages.error(request, 'You must first login.', extra_tags='login')
        return redirect('/')
    user_id = int(request.session['user_id'])
    user = User.objects.get_user(user_id)
    posts = Post.objects.get_friends_posts(user_id)
    friends = Friendship.objects.get_user_friends(user)
    posts_with_likes = []
    for post in posts:
        post_data = {
            'post': post,
            'has_liked': Like.objects.has_user_liked_post(post.id, user_id)
        }
        if post.shared:
            shared_post = Post.objects.filter(id=post.shared_post_id).first()
            if shared_post:
                post_data['shared_post'] = shared_post
        posts_with_likes.append(post_data)
    friend_requests = FriendRequest.objects.get_friend_requests(user)
    context = {
        'posts_with_likes': posts_with_likes,
        'user': user,
        'friends': friends,
        'has_friend_requests': friend_requests.exists(),
        'friend_requests': friend_requests,
    }
    return render(request, 'home_page.html', context)

def view_edit_profile_page(request):
    if not 'user_id' in request.session:
        messages.error(request, 'You must first login.', extra_tags='login')
        return redirect('/')
    user = User.objects.get_user(int(request.session['user_id']))
    personal_detials = PersonalDetails.objects.get(user=user)
    friends = Friendship.objects.get_user_friends(user)
    context = {
        'user': user,
        'friends': friends,
        'personal_details': personal_detials,
    }
    return render(request, 'edit_profile.html', context)

def view_post(request, id=0):
    if not 'user_id' in request.session:
        messages.error(request, 'You must first login.', extra_tags='login')
        return redirect('/')
    if id == 0:
        post = Post.objects.get_post(int(request.POST['post_id']))
    else:
        post = Post.objects.get_post(id)
    if post.shared:
        shared_post = Post.objects.get_post(post.shared_post_id)
    else:
        shared_post = 0
    context = {
        'post': post,
        'has_user_liked_post': Like.objects.has_user_liked_post(id, int(request.session['user_id'])),
        'user': User.objects.get_user(int(request.session['user_id'])),
        'shared_post': shared_post,
    }
    return render(request, 'view_post.html', context)

def view_profile(request, id):
    if not 'user_id' in request.session:
        messages.error(request, 'You must first login.', extra_tags='login')
        return redirect('/')
    current_user = User.objects.get_user(int(request.session['user_id']))
    user = User.objects.get_user(id)
    personal_detials = PersonalDetails.objects.get(user=user)
    friends = Friendship.objects.get_user_friends(user)
    is_friends_with_user = Friendship.objects.is_friends_with_user({'user_1': user.id, 'user_2': int(request.session['user_id'])})
    posts = Post.objects.get_user_posts(id)
    posts_with_likes = []
    for post in posts:
        post_data = {
            'post': post,
            'has_liked': Like.objects.has_user_liked_post(post.id, int(request.session['user_id']))
        }
        if post.shared:
            shared_post = Post.objects.filter(id=post.shared_post_id).first()
            if shared_post:
                post_data['shared_post'] = shared_post
        posts_with_likes.append(post_data)
    context = {
        'user': user,
        'posts_with_likes': posts_with_likes,
        'friends': friends,
        'personal_details': personal_detials,
        'is_friends_with_user': is_friends_with_user,
        'friends_count': len(friends),
        'has_sent_a_friend_request_to_user': FriendRequest.objects.has_sent_a_friend_request_to_user({'user': current_user, 'other_user': user}),
        'has_received_a_friend_request_from_user': FriendRequest.objects.has_received_a_friend_request_from_user({'user': user, 'other_user': current_user}),
    }
    return render(request, 'view_profile.html', context)

def get_messages(request, friend_id):
    recipient = User.objects.get(id=friend_id)
    user_id = request.session['user_id']
    sender = User.objects.get_user(user_id)
    from django.db.models import Q
    messages = Message.objects.filter(
        (Q(sender=sender) & Q(recipient=recipient)) |
        (Q(sender=recipient) & Q(recipient=sender))
    ).order_by('created_at')
    message_data = [
        {'sender': message.sender.id, 'content': message.content, 'created_at': message.created_at.strftime('%Y-%m-%d %H:%M')}
        for message in messages
    ]
    return JsonResponse({'messages': message_data})

def like_post(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        post_id = request.POST.get('post_id')
        user_id = request.session.get('user_id')

        if not post_id or not user_id:
            return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

        post = Post.objects.get_post(post_id)
        user = User.objects.get_user(user_id)

        # Toggle the like status
        if post.likes.filter(user=user).exists():
            Like.objects.remove_like(post_id, user_id)
            liked = False
        else:
            Like.objects.add_like(post_id, user_id)
            liked = True
        like_count = post.likes.count()

        # Return the response
        return JsonResponse({
            'success': True,
            'liked': liked,
            'like_count': like_count,
        })

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

def create_post(request):
    if request.method == 'POST':
        if not 'user_id' in request.session:
            messages.error(request, 'You must first login.', extra_tags='login')
            return redirect('/')
        errors = Post.objects.basic_validator(request.POST)
        if errors:
            for key, value in errors.items():
                messages.error(request, value, extra_tags='create_post')
            redirect_target = 'view_profile' if request.POST['current_view'] != 'home' else 'home'
            profile_id = int(request.POST.get('current_view')) if request.POST.get('current_view') != 'home' else 0
            return redirect(redirect_target, id=profile_id) if redirect_target == 'view_profile' else redirect(redirect_target)
        user_id = request.session['user_id']
        user = User.objects.get_user(user_id)
        Post.objects.create_post({'content': request.POST['content'], 'creator': user, 'shared': False, 'shared_post_id': 0})
        redirect_target = 'view_profile' if request.POST['current_view'] != 'home' else 'home'
        profile_id = int(request.POST.get('current_view')) if request.POST.get('current_view') != 'home' else 0
        return redirect(redirect_target, id=profile_id) if redirect_target == 'view_profile' else redirect(redirect_target)
    return redirect('home')

def share_post(request):
    if request.method == 'POST':
        if not 'user_id' in request.session:
            messages.error(request, 'You must first login.', extra_tags='login')
            return redirect('/')
        user_id = request.session['user_id']
        user = User.objects.get_user(user_id)
        shared_post_id = int(request.POST['post_id'])
        shared_post = Post.objects.get_post(shared_post_id)
        Post.objects.create_post({'content': shared_post.content, 'creator': user, 'shared': True, 'shared_post_id': shared_post_id})
        redirect_target = 'view_profile' if request.POST['current_view'] == 'view_profile' else 'home'
        profile_id = int(request.POST.get('current_profile')) if request.POST.get('current_profile') else 0
        return redirect(redirect_target, id=profile_id) if redirect_target == 'view_profile' else redirect(redirect_target)
    return redirect('home')

def delete_post(request):
    if 'user_id' not in request.session:
        return JsonResponse({'success': False, 'error': 'You must first login.'}, status=401)
    post_id = request.POST.get('post_id')
    post = Post.objects.get(id=post_id)
    if post.creator.id != int(request.session['user_id']):
        return JsonResponse({'success': False, 'error': 'You cannot delete a post which you have not created.'}, status=403)
    post.delete()
    current_view = request.POST.get('current_view', 'home')
    profile_id = int(request.POST.get('current_profile', 0))
    return JsonResponse({'success': True, 'current_view': current_view, 'profile_id': profile_id})

def delete_post_view_post_view(request):
    if not 'user_id' in request.session:
        messages.error(request, 'You must first login.', extra_tags='login')
        return redirect('/')
    id = int(request.POST['post_id'])
    post = Post.objects.get_post(id)
    if post.creator.id != int(request.session['user_id']):
        messages.error(request, 'You cannot delete a post which you have not created.', extra_tags='post')
        redirect_target = 'view_profile' if request.POST['current_view'] == 'view_profile' else 'home'
        profile_id = int(request.POST.get('current_profile')) if request.POST.get('current_profile') else 0
        return redirect(redirect_target, id=profile_id) if redirect_target == 'view_profile' else redirect(redirect_target)
    Post.objects.delete_post(id)
    redirect_target = 'view_profile' if request.POST['current_view'] == 'view_profile' else 'home'
    profile_id = int(request.POST.get('current_profile')) if request.POST.get('current_profile') else 0
    return redirect(redirect_target, id=profile_id) if redirect_target == 'view_profile' else redirect(redirect_target)

def add_comment(request):
    if request.method == 'POST':
        if not 'user_id' in request.session:
            messages.error(request, 'You must first login.', extra_tags='login')
            return redirect('/')
        content = request.POST['content']
        post_id = request.POST['post_id']
        errors = Comment.objects.basic_validator({'content': content})
        if errors:
            for key, value in errors.items():
                messages.error(request, value, extra_tags='comment')
            return redirect('view_post', id=post_id)
        user = User.objects.get_user(int(request.session['user_id']))
        post = Post.objects.get_post(post_id)
        Comment.objects.create_comment({'content': content, 'user': user, 'post': post})
        return redirect('view_post', id=post_id)
    return redirect('home')

def delete_comment(request):
    if not 'user_id' in request.session:
        messages.error(request, 'You must first login.', extra_tags='login')
        return JsonResponse({'success': False, 'error': 'You must first login.'})
    id = request.POST['comment_id']
    comment = Comment.objects.get(id=id)
    if comment.commentor.id != request.session['user_id']:
        messages.error(request, 'You cannot delete a comment which you have not created.', extra_tags='comment')
        return JsonResponse({'success': False, 'error': 'You cannot delete a comment which you have not created.'})
    comment.delete()
    return JsonResponse({'success': True, 'message': 'Comment deleted successfully.'})

@csrf_exempt
def send_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        recipient = User.objects.get(id=int(data['receiver']))
        user_id = request.session['user_id']
        sender = User.objects.get_user(user_id)
        Message.objects.create(
            sender=sender,
            recipient=recipient,
            content=data['content']
        )
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Unauthorized'}, status=401)

def update_activity(request):
    user = User.objects.get(id=int(request.session['user_id']))
    User.objects.update_user_activity(user)
    return JsonResponse({'status': 'success'})

def view_messages(request, friend_id):
    if not 'user_id' in request.session:
        messages.error(request, 'You must first login.', extra_tags='login')
        return redirect('/')
    user_id = request.session['user_id']
    messages = Message.objects.get_messages({'user_id': user_id, 'friend_id': friend_id})
    friend = User.objects.get_user(friend_id)
    context = {
        'messages': messages,
        'friend': friend,
    }
    return render(request, 'messages.html', context)

def add_friend(request):
    if request.method == 'POST':
        if not 'user_id' in request.session:
            messages.error(request, 'You must first login.', extra_tags='login')
            return redirect('/')
        friend_id = int(request.POST['friend_id'])
        user = User.objects.get(id=int(request.session['user_id']))
        friend = User.objects.get(id=friend_id)
        FriendRequest.objects.create_friend_request({'sender': user, 'recipient': friend})
        return redirect('view_profile', id=friend_id)
    return redirect('home')

def cancel_friend_request(request):
    if request.method == 'POST':
        if not 'user_id' in request.session:
            messages.error(request, 'You must first login.', extra_tags='login')
            return redirect('/')
        friend_id = int(request.POST['sender_id'])
        user = User.objects.get(id=int(request.session['user_id']))
        friend = User.objects.get(id=friend_id)
        FriendRequest.objects.remove_friend_request({'sender': user, 'recipient': friend})
        return redirect('view_profile', id=friend_id)
    return redirect('home')

def respond_to_friend_request(request):
    if request.method == 'POST':
        if not 'user_id' in request.session:
            messages.error(request, 'You must first login.', extra_tags='login')
            return redirect('/')
        friend_id = int(request.POST['sender_id'])
        user = User.objects.get(id=int(request.session['user_id']))
        friend = User.objects.get(id=friend_id)
        if request.POST['response'] == 'accept':
            FriendRequest.objects.accept_friend_request({'sender': friend, 'recipient': user})
        else:
            FriendRequest.objects.remove_friend_request({'sender': friend, 'recipient': user})
        redirect_target = 'view_profile' if request.POST.get('current_view') == 'view_profile' else 'home'
        profile_id = friend_id if request.POST.get('current_view') == 'view_profile' else 0
        return redirect(redirect_target, id=profile_id) if redirect_target == 'view_profile' else redirect(redirect_target)
    return redirect('home')

def remove_friend(request):
    if request.method == 'POST':
        if not 'user_id' in request.session:
            messages.error(request, 'You must first login.', extra_tags='login')
            return redirect('/')
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            friend_id = request.POST.get('friend_id')
            user = User.objects.get(id=request.session['user_id'])
            friend = User.objects.get(id=friend_id)
            Friendship.objects.remove_friendship({'user_1': user.id, 'user_2': friend.id})
            return JsonResponse({'success': True, 'friend_id': friend_id})
        else:
            friend_id = request.POST.get('friend_id')
            user = User.objects.get(id=int(request.session['user_id']))
            friend = User.objects.get(id=friend_id)
            Friendship.objects.remove_friendship({'user_1': user.id, 'user_2': friend.id})
            return redirect('view_profile', id=friend_id)
    return JsonResponse({'success': False, 'error': 'Invalid request.'}, status=400)

def search_user(request):
    if request.method == 'POST':
        if 'user_id' not in request.session:
            messages.error(request, 'You must first login.', extra_tags='login')
            return redirect('/')
        search_results = User.objects.search(request.POST['search'])
        user_ids = [user.id for user in search_results]
        request.session['search_results'] = user_ids
        request.session['search_term'] = request.POST['search']
        return redirect('search_results')
    return redirect('home')

def view_search_results(request):
    if 'user_id' not in request.session:
        messages.error(request, 'You must first login.', extra_tags='login')
        return redirect('/')
    user_id = int(request.session['user_id'])
    user = User.objects.get(id=user_id)
    friends = Friendship.objects.get_user_friends(user)
    search_results = User.objects.filter(id__in=request.session['search_results'])
    context = {
        'user': user,
        'friends': friends,
        'search_results': search_results,
        'search_term': request.session['search_term'],
    }
    return render(request, 'search_results.html', context)

def edit_comment(request):
    if request.method == 'POST':
        if not 'user_id' in request.session:
            return JsonResponse({'success': False, 'error': 'You must first login.'})
        comment_id = request.POST['comment_id']
        comment = Comment.objects.get(id=comment_id)
        if comment.commentor.id != int(request.session['user_id']):
            return JsonResponse({'success': False, 'error': 'You cannot edit a comment that you did not create.'})
        content = request.POST['content']
        errors = Comment.objects.basic_validator({'content': content})
        if errors:
            return JsonResponse({'success': False, 'errors': errors})
        Comment.objects.update_comment(comment, content)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

def edit_post(request):
    if not 'user_id' in request.session:
        messages.error(request, 'You must first login.', extra_tags='login')
        return redirect('/')
    post_id = request.POST.get('post_id')
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Post not found'}, status=404)
    if post.creator.id != int(request.session['user_id']):
        messages.error(request, 'You cannot edit a post that you did not create.', extra_tags='edit_post')
        return redirect('view_post', id=post_id)
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        content = request.POST.get('content')
        if content:
            post.content = content
            post.save()
            return JsonResponse({
                'status': 'success',
                'content': post.content
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'No content provided'
            })
    return redirect('home')

def update_profile(request):
    if request.method == 'POST':
        if not 'user_id' in request.session:
            messages.error(request, 'You must first login.', extra_tags='login')
            return redirect('/')
        user = User.objects.get(id=int(request.session['user_id']))
        profile_pic = request.FILES.get('profile_pic')
        if profile_pic:
            fs = FileSystemStorage()
            filename = fs.save(profile_pic.name, profile_pic)
            file_url = fs.url(filename).lstrip('/media')
            user.profile_picture = file_url
            user.save()
        personal_details_data = {
            'user': user,
            'bio': request.POST.get('bio', '').strip(),
            'location': request.POST.get('location', '').strip(),
            'workplace': request.POST.get('workplace', '').strip(),
            'phone_number': request.POST.get('phone_number', '').strip(),
            'relationship_status': request.POST.get('relationship_status', '').strip(),
        }
        errors = PersonalDetails.objects.basic_validator(personal_details_data)
        if errors:
            for key, value in errors.items():
                messages.error(request, value, extra_tags='edit_profile')
            return redirect('view_edit_profile_page')
        PersonalDetails.objects.update_personal_details_record(personal_details_data)
        user_data = {
            'user': user,
            'id': user.id,
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name'),
            'current_password': request.POST.get('current_password'),
            'new_password': request.POST.get('new_password'),
            'confirm_new_password': request.POST.get('confirm_new_password'),
            'email': request.POST.get('email'),
        }
        errors = User.objects.update_data_validator(user_data)
        if errors:
            for key, value in errors.items():
                messages.error(request, value, extra_tags='edit_profile')
            return redirect('view_edit_profile_page')
        User.objects.update_user_data(user_data)
        return redirect('view_profile', id=user.id)
    return redirect('home')

def generate_qr_code(request, user_id):
    user = User.objects.get(id=user_id)
    add_friend_url = request.build_absolute_uri(reverse('add_friend_qr', args=[user_id]))
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(add_friend_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    response = HttpResponse(content_type="image/png")
    img.save(response, "PNG")
    return response

def add_friend_qr(request, user_id):
    if not 'user_id' in request.session:
        messages.error(request, 'You must be logged in first.', extra_tags='login')
        return redirect('/')
    current_user_id = request.session['user_id']
    if current_user_id == user_id:
        messages.error(request, "You cannot add yourself as a friend.")
        return redirect('home')
    try:
        friend_user = User.objects.get(id=user_id)
        current_user = User.objects.get(id=current_user_id)
        FriendRequest.objects.create_friend_request({'recipient': friend_user, 'sender': current_user})
        messages.success(request, f"A friend request has been sent to {friend_user.first_name} {friend_user.last_name}!", extra_tags='success')
    except User.DoesNotExist:
        messages.error(request, "User not found.", extra_tags='error')
    return redirect('home')