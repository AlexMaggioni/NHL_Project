# IFT6758_NHL

Ne pas oublier de modifier l'emplacement où les données vont être téléchargé dans .env (changer DATA_FOLDER).

## Filetree Structure

Tous les scripts et notebooks pour l'evaluation de la Milestone 1, sont dans le rep `Milestone1`

Et le rapport en style d'articles de blog sont dans `blog_website/milestone1/_posts/`. Vous pouvez aussi run `bundle exec jekyll serve autoreload & ` dans `blog_website`

## jelkyll blog website

### To add new blog to the blog website:

```bash
	cd blog_website
```

```
bundle exec jekyll serve autoreload &
```

You will be prompt with an URL...

Then to add a new blog :

* create a new dir `{new_category_posts}/_posts` and **`.md` files needs to start with this format `YYYY-MM-DD-filename.md` to be recognized as new blog**

---
