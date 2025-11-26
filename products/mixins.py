
class TitleContextMixin:
    def get_titles_with_status(self, titles):
        titles_with_status = []
        for title in titles:
            titles_with_status.append({
                'title': title,
                'status': title.get_user_status(self.request.user),
                'image_url': title.get_image_url()
            })
        return titles_with_status
