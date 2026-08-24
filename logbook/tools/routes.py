# -*- encoding: utf-8 -*-
"""
tools/my-tools/
"""

from datetime import datetime
from flask import current_app, render_template, request, url_for, redirect, jsonify
from flask_login import login_required, current_user
from imagekitio import ImageKit
from werkzeug.utils import secure_filename
#from werkzeug.exceptions import RequestEntityTooLarge

from ..utilities import role_required, get_segment
from . import blueprint
from .forms import AddNewTool, UploadImageForm, ToolTagForm
from .models import CordedTool, RegisteredTool, CordedToolTag, ImagekitFile


# Views
@blueprint.get('/my-tools')
@login_required
@role_required('foreman', 'admin')
def index():

    toolbox = RegisteredTool.find_by_concretor(current_user.id)
    tagsbox = {tool.id: CordedToolTag.find_by_toolid(tool.id) for tool in toolbox}
    
    return render_template('tools/index.html',
                           segment = get_segment(request),
                           tools = toolbox,
                           tags = tagsbox,
                           datetimenow = datetime.now()
                           )
    
@blueprint.route('/my-tools/new', methods=['GET', 'POST'])
@login_required
@role_required('foreman', 'admin')
def add_tool():

    addTool = AddNewTool()

    if addTool.validate_on_submit():
        newTool = {
            "brand_name": addTool.brand.data,
            "model_number": addTool.model.data,
            "tool_name": addTool.tool.data,
            "tool_type": addTool.tool_type.data,
            "serial_num": addTool.serial.data,
            "ht_num": addTool.hilti.data,
            "tool_notes": addTool.notes.data,
            "added_by": current_user.id
        }
        
        # register new tool
        if addTool.tool_type.data == 'corded':
            tool = CordedTool(**newTool)
        else:
            tool = RegisteredTool(**newTool)
        
        #return jsonify(tool.to_json())
        tool.save()

        return redirect(url_for('.index'))

    return render_template('tools/register-tool.html', toolform=addTool)

@blueprint.route('/my-tools/<string:_id>', methods=['GET', 'POST'])
@login_required
@role_required('foreman', 'admin')
def view_tool(_id):

    uploadImage = UploadImageForm()
    tagTool = ToolTagForm()
    if (tool:= RegisteredTool.find_by_id(tool_id=_id)).tool_type == "corded":
        tool = CordedTool.find_by_id(tool_id=_id)
        tag = CordedToolTag.find_by_toolid(tool=tool.id) # should exist for all tools
    else:
        tag = None
    image = ImagekitFile.find_by_toolid(_id)

    if uploadImage.validate_on_submit():
        f = uploadImage.upload.data
        imageKit = make_imagekit()

        if image:
            imageKit.files.delete(image.file_id)
        
        # Generate a unique filename to avoid overwrites
        safe_filename = secure_filename(f.filename)
        unique_filename = generate_unique_filename(safe_filename)        

        # Upload from bytes (web forms)
        try:
            response = imageKit.files.upload(
                file = f.read(),
                file_name = unique_filename
            )
        except Exception as e:
            print(f"ImageKit Error: {e}")
            return (
                jsonify({"success": False, "error": "Failed to upload data"}),
                500,
            )

        response_details = {
            "tool_id": tool.id,
            "file_id": response.file_id,
            "file_url": response.url
            }
        
        save_metadata(response_details)

        return redirect(url_for('.view_tool', _id=_id))

    elif tagTool.validate_on_submit():

        newTag = {
            "tool_id": tool.id,
            "tag_num": tagTool.tag_num.data or None,
            "tag_date": tagTool.tag_date.data,
            "next_test": tagTool.next_test.data or None
        }
        #return jsonify(newTag)
        newTag = CordedToolTag(**newTag)# without init() all parameters must be supplied
        newTag.save()
        tool.update_tag(newTag.id)

        return redirect(url_for('.view_tool', _id=_id))

    
    return render_template('tools/view-tool.html',
                           segment = 'my-tools',
                           tool = tool,
                           tag = tag,
                           url = image.file_url if image else None,
                           fileform = uploadImage,
                           tagform = tagTool,
                           datetimenow = datetime.now()
                           )

@blueprint.get('/my-tools/<string:_id>/del')
@login_required
@role_required('foreman', 'admin')
def delete_tool(_id):

    """  Remove tool from register.  """
    tool = RegisteredTool.find_by_id(tool_id=_id)
    tool.delete_from_db()

    return redirect(url_for('.index'))

@blueprint.post('/my-tools/<string:_id>/tag')
@login_required
@role_required('admin')
def tag_tool(_id):

    """  Tag tool with today's date, within main table."""
    newTag = CordedToolTag(tool_id=_id, tag_date=datetime.now())
    newTag.save()
    tool = CordedTool.find_by_id(tool_id=_id)
    tool.update_tag(newTag.id)
    print("Success! Tool tagged with today's date.", newTag)
    
    return redirect(url_for('.index', _id=_id))

#******************************************************************************
# Admin View
@blueprint.get('/all-tools')
@login_required
@role_required('foreman', 'admin')
def all_tools():

    page_num = request.args.get('page', 1, type=int)
    show = 5
    entries = RegisteredTool.query.paginate(page=page_num, per_page=show, error_out=False)

    return render_template('tools/all-tools.html',
                           admin = True,
                           title = "Tool Register",
                           subtitle = "All registered tools.",
                           tools = entries,
                           segment='query',
                           page=page_num,
                           per_page=show
    )

#******************************************************************************
# Errors

@blueprint.errorhandler(403)
def access_forbidden(error):
    print(error)
    return render_template('home/page-403.html'), 403

#******************************************************************************
# Helpers

# 2. Save metadata after client confirms successful upload to ImageKit

def save_metadata(details):

    toolImage = ImagekitFile.find_by_toolid(details['tool_id'])
    if toolImage:
        try:
            toolImage.update_image(details)

        except Exception as e:
            print(f"Unexpected Metadata Update Error: {e}")
            return jsonify({"success": False, "error": "Server error"}), 500
    else:
        try:
            new_tool_image = ImagekitFile(
                tool_id = details.get('tool_id'),
                file_id = details.get('file_id'),
                file_url=details.get('file_url')
            )
            new_tool_image.save()

            print(f"Metadata saved for ImageKit file: {details.get('file_id')}")
            return jsonify({"success": True}), 201
        except Exception as e:
            print(f"Unexpected Metadata Save Error: {e}")
            return jsonify({"success": False, "error": "Server error"}), 500    


# Make Image Kit
def make_imagekit():

    image_kit = ImageKit(
        private_key = current_app.config.get("IMAGEKIT_SECRET")
    )
    return image_kit
 

# Generate unique filename
import uuid
def generate_unique_filename(original_filename):
    """
    Generate a unique filename while preserving the extension,
    to avoid collisions.
    """
    # Extract extension from original filename
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
    
    return f"{uuid.uuid4().hex}.{ext}"
