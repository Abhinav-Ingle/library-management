from ninja import NinjaAPI
#import routers from all the views.
from MyLib.views.apiBook import bookRouter
from MyLib.views.apiAuthor import authorRouter
from MyLib.views.apiBorrower import borrowerRouter
#initialise the app url collector.
api = NinjaAPI()
#In case of multiple apps, it is recommended to group urls of one app together.
#adding the first root from the only available app.

api.add_router("/book/",bookRouter)
api.add_router("/author/",authorRouter)
api.add_router("/borrower/",borrowerRouter)