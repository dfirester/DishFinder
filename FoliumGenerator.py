import numpy as np
import pandas as pd
import geopandas
import folium
from folium.plugins import HeatMap
from folium.plugins import MarkerCluster


class FoliumMapGenerator(object):
    def __init__(self):
        pass


    def pre_loaded(self,food):
        name = food + '.csv'
        tacos = pd.read_csv(name)
        tacos = tacos.set_index('name')
        f = self._get_map(tacos)
        return f, tacos


    def fastsearch_map(self,food,user):
        tacos = self._fast_search(food,user)
        f = self._get_map(tacos)
        return f, tacos



    def _fast_search(self,keyword,user):
        keyword = keyword.lower().strip()
        if keyword[-1] == 's':
            keyword = keyword[:-1]
        
        
        df = pd.read_csv('toronto_0.csv')
        businesses = df[df['text'].str.contains(keyword,regex=True)]['business_id'].value_counts().index.to_list()
        try:
            businesses = businesses[:10]
        except:
            businesses = businesses
        foodscore_dict = {}
        fooddiv_dict = {}
        ratio_dict = {}
        userrating_dict = {}

        for business in businesses:
            sb = df[df['business_id'] == business]
            allstars = sb.stars_y.to_list()
            fooditem_stars = sb[sb['text'].str.contains(keyword,regex=True)].stars_y.to_list()
            totscore = np.mean([np.mean(allstars), np.mean(fooditem_stars)])
            foodscore_dict.update({business : totscore})
            ratio_dict.update({business : len(fooditem_stars)/len(allstars)})
            name = sb['name'].to_list()[0]
            userrating_dict.update({business : user.expectedreview(business)})
        

        df['taco'+' score'] = df['business_id'].map(foodscore_dict)
        df['taco'+' ratio'] = df['business_id'].map(ratio_dict)
        df['exp_user_review'] = df['business_id'].map(userrating_dict)

        
        newdf = df.groupby('name').mean().sort_values('taco'+' score',ascending=False)
        newdf = newdf[newdf['taco'+ ' score'].notna()]
        busidcol = [df[df['name'] == newdf.index[i]]['business_id'].values[0] for i in range(len(newdf.index))]
        address = [df[df['name'] == newdf.index[i]]['address'].values[0] for i in range(len(newdf.index))]
        newdf['business_id'] = busidcol
        newdf['address'] = address
        newdf['Weighted ' + 'taco' + ' score'] = newdf['taco' + ' score']*np.exp(newdf['taco' + ' ratio']/2)*np.exp(newdf['exp_user_review'] - 3)
        newdf = newdf.sort_values('Weighted ' + 'taco' + ' score',ascending=False)
        
        storage = newdf.copy()

        for i in range(1,10):
            name = 'toronto_'+str(i)+'.csv'
            df = pd.read_csv(name)
            businesses = df[df['text'].str.contains(keyword,regex=True)]['business_id'].value_counts().index.to_list()
            try:
                businesses = businesses[:10]
            except:
                businesses = businesses
            foodscore_dict = {}
            fooddiv_dict = {}
            ratio_dict = {}
            userrating_dict = {}

            for business in businesses:
                sb = df[df['business_id'] == business]
                allstars = sb.stars_y.to_list()
                fooditem_stars = sb[sb['text'].str.contains(keyword,regex=True)].stars_y.to_list()
                totscore = np.mean([np.mean(allstars), np.mean(fooditem_stars)])
                foodscore_dict.update({business : totscore})
                ratio_dict.update({business : len(fooditem_stars)/len(allstars)})
                name = sb['name'].to_list()[0]
                userrating_dict.update({business : user.expectedreview(business)})
            

            df['taco'+' score'] = df['business_id'].map(foodscore_dict)
            df['taco'+' ratio'] = df['business_id'].map(ratio_dict)
            df['exp_user_review'] = df['business_id'].map(userrating_dict)

            
            newdf = df.groupby('name').mean().sort_values('taco'+' score',ascending=False)
            newdf = newdf[newdf['taco'+ ' score'].notna()]
            busidcol = [df[df['name'] == newdf.index[i]]['business_id'].values[0] for i in range(len(newdf.index))]
            address = [df[df['name'] == newdf.index[i]]['address'].values[0] for i in range(len(newdf.index))]
            newdf['business_id'] = busidcol
            newdf['address'] = address
            newdf['Weighted ' + 'taco' + ' score'] = newdf['taco' + ' score']*np.exp(newdf['taco' + ' ratio']/2)*np.exp(newdf['exp_user_review'] - 3)
            newdf = newdf.sort_values('Weighted ' + 'taco' + ' score',ascending=False)

            storage = pd.concat([storage,newdf])
            
        del newdf
        storage = storage.sort_values('Weighted ' + 'taco' + ' score',ascending=False)
        return storage

    

    def _get_map(self,tacos):
        tacos['Weighted taco score 2'] = (tacos['Weighted taco score'] - min(tacos['Weighted taco score']))/(max(tacos['Weighted taco score']) - min(tacos['Weighted taco score']))
        toptacos = tacos[:10]
        othertacos = tacos[10:]
        gdf_top = geopandas.GeoDataFrame(toptacos, geometry=geopandas.points_from_xy(toptacos.longitude, toptacos.latitude))
        gdf_top.crs = {'init' :'epsg:4326'}

        # Get x and y coordinates for each point
        gdf_top["x"] = gdf_top["geometry"].apply(lambda geom: geom.x)
        gdf_top["y"] = gdf_top["geometry"].apply(lambda geom: geom.y)


        gdf_other = geopandas.GeoDataFrame(othertacos, geometry=geopandas.points_from_xy(othertacos.longitude, othertacos.latitude))
        gdf_other.crs = {'init' :'epsg:4326'}

        # Get x and y coordinates for each point
        gdf_other["x"] = gdf_other["geometry"].apply(lambda geom: geom.x)
        gdf_other["y"] = gdf_other["geometry"].apply(lambda geom: geom.y)

        #First we deal with the not highly rated resturants


        gdf_all = geopandas.GeoDataFrame(tacos, geometry=geopandas.points_from_xy(tacos.longitude, tacos.latitude))
        gdf_all.crs = {'init' :'epsg:4326'}

        # Get x and y coordinates for each point
        gdf_all["x"] = gdf_all["geometry"].apply(lambda geom: geom.x)
        gdf_all["y"] = gdf_all["geometry"].apply(lambda geom: geom.y)

        # Create a list of coordinate pairs
        locations_with_weights = list(zip(gdf_all["y"], gdf_all["x"],np.exp((5*gdf_other['Weighted taco score 2'] - .3))))

        locations = list(zip(gdf_other["y"], gdf_other["x"]))


        m = folium.Map(location=[43.65,-79.38], tiles = 'cartodbpositron', zoom_start=11, control_scale=True)
        html = """Resturant Name: <td>{}</td><br> Food Score: <td>{}</td>""".format

        width, height = 300,50
        popups, locations,icons = [], [],[]

        for idx, row in gdf_other.iterrows():
            locations.append([row['geometry'].y, row['geometry'].x])
            name = idx

            iframe = folium.IFrame(html(name,round(row['Weighted taco score'],3)), width=width, height=height)
            popups.append(folium.Popup(iframe))
            icons.append(folium.Icon(icon='info',prefix='fa'))

        h = folium.FeatureGroup(name='Resturant')

        h.add_child(MarkerCluster(locations=locations,icons=icons, popups=popups))
        m.add_child(h)


        points_gjson = folium.features.GeoJson(gdf_other, name="Tacos")
        HeatMap(locations_with_weights,min_opacity=.3).add_to(m)


        #Now we deal with the highly rated resturants
        locations = list(zip(gdf_top["y"], gdf_top["x"]))

        popups, locations,icons = [], [],[]

        for idx, row in gdf_top.iterrows():
            locations.append([row['geometry'].y, row['geometry'].x])
            name = idx

            iframe = folium.IFrame(html(name,round(row['Weighted taco score'],3)), width=width, height=height)
            popups.append(folium.Popup(iframe))
            icons.append(folium.Icon(color='lightred',icon='thumbs-up',prefix='fa'))

        h2 = folium.FeatureGroup(name='Top Resturant')
        for i in range(len(icons)):
            h2.add_child(folium.Marker(location=locations[i],icon=icons[i],popup=popups[i]))

        m.add_child(h2)
        #m.save('templates/map.html')
        f = folium.Figure(width=500, height=500)
        m.add_to(f)
        return f
