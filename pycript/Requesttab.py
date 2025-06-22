from burp import IMessageEditorTab
from pycript.Reqcheck import DecryptRequest,EncryptRequest
import json
from array import array


class CriptInputTab(IMessageEditorTab):
    def __init__(self, extender, controller, editable):
        self._extender = extender
        self._editable = editable
        self._txtInput = extender.callbacks.createTextEditor()
        self._txtInput.setEditable(editable)
        self.controller = controller
        #self.selectedtab = self._extender.reqresponsecombobox.getSelectedItem()
        self.selectedtab = self._extender.reqresponsecombobox.getSelectedItem()
        extender.callbacks.customizeUiComponent(self._txtInput.getComponent())


    def getTabCaption(self):
        return "PyCript"   


    def getUiComponent(self):
        
        return self._txtInput.getComponent()

    def isEnabled(self, content, isRequest):
        if isRequest:
            if content is None:
                return False

            if str(self._extender.selectedrequesttpye) == "None" or str(self._extender.reqresponsecombobox.getSelectedItem()) == "Response":
                return False

            return True
        return False 


    # def setMessage(self, content, isRequest):
    #     if content is None:
    #         self._txtInput.setText(None)
    #         self._txtInput.setEditable(False)
    #     else:
    #         if isRequest:
    #             if self.controller.getHttpService() is not None:
    #                 url = self._extender.helpers.analyzeRequest(
    #                     self.controller.getHttpService(), self.controller.getRequest()
    #                 ).getUrl()

    #                 if self._extender.callbacks.isInScope(url):
    #                     request = self._extender.helpers.analyzeRequest(content)
    #                     output = DecryptRequest(self._extender, content, request)

    #                     if output is None:
    #                         output = "Error: Decryption returned no data".encode('utf-8')
    #                     elif isinstance(output, array):
    #                         output = output.tostring()
    #                     elif isinstance(output, unicode):
    #                         output = output.encode('utf-8')

    #                     try:
    #                         request_info = self._extender.helpers.analyzeRequest(output)
    #                         body_offset = request_info.getBodyOffset()
    #                         full_str = self._extender.helpers.bytesToString(output)
    #                         body = full_str[body_offset:]
    #                         json_obj = json.loads(body.strip())
    #                         def decode_nested_json(obj):
    #                             if isinstance(obj, dict):
    #                                 return {
    #                                     k: decode_nested_json(json.loads(v)) if isinstance(v, basestring) and v.strip().startswith('{') else v
    #                                     for k, v in obj.items()
    #                                 }
    #                             elif isinstance(obj, list):
    #                                 return [decode_nested_json(item) for item in obj]
    #                             return obj

    #                         try:
    #                             json_obj = decode_nested_json(json_obj)
    #                         except Exception as e:
    #                             print("[PyCript DEBUG] Nested decoding failed:", str(e))

    #                         pretty = json.dumps(json_obj, indent=4)
    #                         pretty_bytes = pretty.replace('\n', '\r\n').encode('utf-8')



    #                         output = self._extender.helpers.buildHttpMessage(
    #                             request_info.getHeaders(),
    #                             pretty_bytes
    #                         )
    #                     except Exception as e:
    #                         print("[PyCript DEBUG] JSON body formatting failed:", str(e))

    #                 else:
    #                     output = "URL is not added in Scope".encode('utf-8')
    #                     self._txtInput.setEditable(False)

    #                 self._txtInput.setText(output)
    #                 self._txtInput.setEditable(True)

    #     self._currentMessage = content


    def setMessage(self, content, isRequest):
        if content is None:
            self._txtInput.setText(None)
            self._txtInput.setEditable(False)
        else:
            if isRequest:
                if self.controller.getHttpService() is not None:
                    url = self._extender.helpers.analyzeRequest(
                        self.controller.getHttpService(), self.controller.getRequest()
                    ).getUrl()

                    if self._extender.callbacks.isInScope(url):
                        request = self._extender.helpers.analyzeRequest(content)
                        output = DecryptRequest(self._extender, content, request)

                        if output is None:
                            output = "Error: Decryption returned no data".encode('utf-8')
                        elif isinstance(output, array):
                            output = output.tostring()
                        elif isinstance(output, unicode):
                            output = output.encode('utf-8')

                        try:
                            request_info = self._extender.helpers.analyzeRequest(output)
                            headers = request_info.getHeaders()
                            body_offset = request_info.getBodyOffset()
                            full_str = self._extender.helpers.bytesToString(output)
                            body = full_str[body_offset:]

                            json_obj = json.loads(body.strip())

                            def recursive_format(obj):
                                if isinstance(obj, dict):
                                    for k, v in obj.items():
                                        if isinstance(v, basestring) and v.strip().startswith('{') and v.strip().endswith('}'):
                                            try:
                                                inner_obj = json.loads(v)
                                                obj[k] = recursive_format(inner_obj)
                                            except:
                                                pass
                                        elif isinstance(v, (dict, list)):
                                            obj[k] = recursive_format(v)
                                elif isinstance(obj, list):
                                    for i in range(len(obj)):
                                        item = obj[i]
                                        if isinstance(item, basestring) and item.strip().startswith('{') and item.strip().endswith('}'):
                                            try:
                                                obj[i] = recursive_format(json.loads(item))
                                            except:
                                                pass
                                        elif isinstance(item, (dict, list)):
                                            obj[i] = recursive_format(item)
                                return obj

                            json_obj = recursive_format(json_obj)

                            pretty = json.dumps(json_obj, indent=4)
                            pretty_bytes = pretty.replace('\n', '\r\n').encode('utf-8')

                            output = self._extender.helpers.buildHttpMessage(headers, pretty_bytes)

                        except Exception as e:
                            print("[PyCript DEBUG] JSON formatting failed:", str(e))

                    else:
                        output = "URL is not added in Scope".encode('utf-8')
                        self._txtInput.setEditable(False)

                    self._txtInput.setText(output)
                    self._txtInput.setEditable(True)

        self._currentMessage = content






    
    def getMessage(self):
        if self._txtInput.isTextModified():
            editable_bytes = self._txtInput.getText()
            editable_str = self._extender.helpers.bytesToString(editable_bytes)

            try:
                request_info = self._extender.helpers.analyzeRequest(editable_bytes)
                body_offset = request_info.getBodyOffset()
                headers = request_info.getHeaders()
                body = editable_str[body_offset:]

                # Attempt to minify the JSON body before encrypting
                json_obj = json.loads(body)
                compact_body = json.dumps(json_obj, separators=(',', ':'))
                compact_bytes = compact_body.encode('utf-8')

                # Rebuild the message with original headers and compacted body
                editable_bytes = self._extender.helpers.buildHttpMessage(headers, compact_bytes)

            except Exception as e:
                print("[PyCript DEBUG] Error compacting body before encryption:", str(e))
                # fallback: use as-is

            req = self._extender.helpers.analyzeRequest(editable_bytes)
            output = EncryptRequest(self._extender, editable_bytes, req)
            return output

        else:
            return self._currentMessage

    
    
    
    def isModified(self):
        return self._txtInput.isTextModified()
    
    def getSelectedData(self):
        return self._txtInput.getSelectedText()                


