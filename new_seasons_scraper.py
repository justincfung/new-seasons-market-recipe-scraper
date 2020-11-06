import os
import csv
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


def write_to_file(outfile, var, header):
    if os.path.isfile(outfile):
        with open(outfile, 'a', newline='', encoding='utf-8') as result:
            writer = csv.writer(result)
            writer.writerow(var)
    else:
        with open(outfile, 'w', newline='', encoding='utf-8') as result:
            writer = csv.writer(result)
            writer.writerow(header)
            writer.writerow(var)


def new_seasons_recipe_scraper(file_folder, new_season_category_outfile, new_season_recipe_outfile, new_seasons_full):
    driver = webdriver.Chrome()
    driver.get('https://www.newseasonsmarket.com/recipes/')
    items = driver.find_elements_by_xpath("//a[@class='recipetitle']")
    category_pages = {item.text: item.get_attribute('href') for item in items}
    categories = list(category_pages.keys())
    category_links = list(category_pages.values())
    all_recipes = {}
    for counter in range(0, len(category_pages)):
        driver.get(category_links[counter])
        recipe_page = driver.find_elements_by_xpath(
            "//div[@class='column1stuff col-xs-12 col-md-4']//descendant::div/descendant::a")
        recipe_dict = {recipe.text: recipe.get_attribute('href') for recipe in recipe_page}
        try:
            next_page = driver.find_element_by_xpath("//a[@class='next']").get_attribute('href')
        except NoSuchElementException:
            next_page = False
        while next_page:
            driver.get(next_page)
            other_recipe_page = driver.find_elements_by_xpath(
                "//div[@class='column1stuff col-xs-12 col-md-4']//descendant::div/descendant::a")
            other_recipe_dict = {recipe.text: recipe.get_attribute('href') for recipe in other_recipe_page}
            recipe_dict.update(other_recipe_dict)
            try:
                next_page = driver.find_element_by_xpath("//a[@class='next']").get_attribute('href')
            except NoSuchElementException:
                next_page = False

        category_dict = {categories[counter]: recipe_dict}
        all_recipes.update(category_dict)

    categories = list(all_recipes.keys())
    recipes = list(all_recipes.values())

    for counter in range(0, len(all_recipes)):
        file_name = categories[counter].lower().replace(' ', '_')
        json_folder = 'json'
        file_path = os.path.join(file_folder, json_folder, file_name)
        with open(f'{file_path}.json', 'w') as outfile:
            json.dump(recipes[counter], outfile)

    index = 100000
    for counter in range(0, len(all_recipes)):
        category = categories[counter]
        recipe = recipes[counter]
        recipe_names = list(recipe.keys())
        recipe_links = list(recipe.values())

        for inner_counter in range(0, len(recipe)):
            var = [index, category]
            header = ['new_seasons_id', 'category']
            write_to_file(os.path.join(file_folder, new_season_category_outfile), var, header)
            index += 1

    index = 100000
    for recipe in recipes:
        recipe_names = list(recipe.keys())
        recipe_links = list(recipe.values())
        for counter in range(0, len(recipe)):
            driver.get(recipe_links[counter])
            try:
                recipe_image = driver.find_element_by_xpath("//img[@class='recipe-image']")
                recipe_image = recipe_image.get_attribute('src') if recipe_image else None
            except NoSuchElementException:
                recipe_image = None
            try:
                directions = driver.find_elements_by_xpath("//ol[@class='steps']//descendant::li/descendant::p")
                directions = [direction.text for direction in directions]
            except NoSuchElementException:
                directions = None
            try:
                ingredients = driver.find_elements_by_xpath("//ul[@class='ingredientlist']//descendant::li")
                ingredients = [ingredient.text for ingredient in ingredients]
            except NoSuchElementException:
                ingredients = None
            var = [index, recipe_names[counter], recipe_links[counter], recipe_image, ingredients, directions]
            header = ['new_seasons_id', 'recipe_name', 'recipe_link', 'recipe_image', 'ingredients', 'directions']
            write_to_file(os.path.join(file_folder, new_season_recipe_outfile), var, header)
            index += 1

    driver.close()

    category_mapping = pd.read_csv(os.path.join(file_folder, new_season_category_outfile))
    recipe_details = pd.read_csv(os.path.join(file_folder, new_season_recipe_outfile))

    category_mapping.merge(recipe_details, on='new_seasons_id').to_csv(os.path.join(file_folder, new_seasons_full),
                                                                       index=False)


if __name__ == '__main__':
    file_folder = ''  # TODO: Name for the file folder that you want the csv to be written to
    new_season_category_outfile =  # TODO: Name for the category csv
    new_season_recipe_outfile = ''  # TODO: Name for the recipe csv
    new_seasons_full = ''  # TODO: Name for the final csv

    new_seasons_recipe_scraper(file_folder, new_season_category_outfile, new_season_recipe_outfile, new_seasons_full)
print("Process Completed")